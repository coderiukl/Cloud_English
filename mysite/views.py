from django.shortcuts import render
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.http import JsonResponse

from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, LogoutSerializer, ChangePasswordSerializer,
    TopicSerializer, SectionSerializer, SubtopicSerializer, AudioExerciseSerializer
)

from .models import User, Topic, Section, Subtopic, AudioExercise

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):

        # Proceed with the parent method to handle token generation
        try:
            response = super().post(request, *args, **kwargs)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # get email from form submission
        email = request.POST.get('email')
        if email:
            # Add user details to the response

            user = User.objects.get(email=email)
            user_serializer = UserSerializer(user)
            response.data['user'] = user_serializer.data

        return response

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    serializer_class=LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            user.last_login = now()
            user.save(update_fields=['last_login'])

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error':'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAccountView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request':self.request})
        return context
    
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':'Đổi mật khẩu thành công'}, status=status.HTTP_200_OK)

class TopicView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()

class TopicDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, topic_slug, format=None):
        topic = get_object_or_404(Topic, slug=topic_slug)
        query = request.GET.get('q','')
        level = request.GET.get('level','all')

        sections = Section.objects.filter(topic=topic).prefetch_related('subtopics')

        for section in sections:
            subs = section.subtopics.all().order_by('id')

            should_filter = query or (level and level != 'all')

            if should_filter:
                if query:
                    subs = subs.filter(title__icontains=query)
                if level and level != 'all':
                    subs = subs.filter(level=level)
            section.filtered_subtopics = subs

        topic_data = TopicSerializer(topic).data
        return Response({
            'topic':topic_data,
            'sections':SectionSerializer(sections, many=True).data
        })

class ListenAndTypeView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, topic_slug, subtopic_slug, format=None):
        topic = get_object_or_404(Topic, slug=topic_slug)
        subtopic = get_object_or_404(Subtopic, slug=subtopic_slug)
        exercises = AudioExercise.objects.filter(subtopic=subtopic).order_by('position')

        # Chúng ta trả về tên topic, subtopic, và các bài tập
        exercises_data = AudioExerciseSerializer(exercises, many=True).data
        
        return Response({
            'topic': {'name': topic.name, 'slug': topic.slug},
            'subtopic': SubtopicSerializer(subtopic).data,
            'exercises': exercises_data
        })
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_previous_next_subtopic(request, topic_slug, subtopic_id):
    topic = get_object_or_404(Topic, slug=topic_slug)
    current_subtopic = get_object_or_404(Subtopic, id=subtopic_id, topic=topic)

    previous_subtopic = Subtopic.objects.filter(topic=topic, id__lt=current_subtopic.id).order_by('-id').first()
    next_subtopic = Subtopic.objects.filter(topic=topic, id__gt=current_subtopic.id).order_by('id').first()

    return JsonResponse({
        'previous': {
            'id': previous_subtopic.id,
            'slug': previous_subtopic.slug,
            'url': f"/topics/{topic.slug}/subtopics/{previous_subtopic.slug}/listen-and-type/"
        } if previous_subtopic else None,
        'next': {
            'id': next_subtopic.id,
            'slug': next_subtopic.slug,
            'url': f"/topics/{topic.slug}/subtopics/{next_subtopic.slug}/listen-and-type/"
        } if next_subtopic else None
    })

# <Render templates HTML files>
def home_page(request):
    return render(request, 'home.html')

# User template
def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    return render(request, 'register.html')

def change_password_page(request):
    return render(request, 'change_password.html')

def account_page(request):
    return render(request, 'user_account.html')

# Listen templates
def topics_view_page(request):
    return render(request, 'topics_view.html')

def topic_detail_page(request, topic_slug):
    topic = get_object_or_404(Topic,slug=topic_slug)
    sections = Section.objects.filter(topic=topic).prefetch_related('subtopics')
    return render(request, 'topic_detail.html', {'topic':topic, 'sections':sections})

def listen_and_type_page(request, topic_slug, subtopic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)
    subtopic = get_object_or_404(Subtopic, slug=subtopic_slug)

    exercises = AudioExercise.objects.filter(subtopic=subtopic).order_by('id','position')
    return render(
        request,
        'listen_and_type.html',
        {
            'topic':topic,
            'subtopic':subtopic,
            'exercises': exercises
        }
    )

# </Render templates HTML files>