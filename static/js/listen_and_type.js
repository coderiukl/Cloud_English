document.addEventListener("DOMContentLoaded", () => {
  const topicSlug = "{{ topic.slug }}";
  const subtopicSlug = "{{ subtopic.slug }}";

  //   const topicName = document.getElementById('topic-name');
  const subtopicTitle = document.getElementById("subtopic-title");
  const exerciseContent = document.getElementById("exercise-content");
  const exerciseIndex = document.getElementById("exercise-index");
  const exerciseTotal = document.getElementById("exercise-total");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");

  const transcriptList = document.getElementById("transcript-list");
  const fullAudio = document.getElementById("full-audio");
  const autoScroll = document.getElementById("auto-scroll");

  const slideText = document.getElementById("slide-text");
  const slideTrans = document.getElementById("slide-translation");
  const slideIndex = document.getElementById("slide-index");
  const slideTotal = document.getElementById("slide-total");
  const slidePrev = document.getElementById("slide-prev");
  const slideNext = document.getElementById("slide-next");

  let currentIndex = 0;
  let exercises = [];
  const apiUrl = document.getElementById('api-url').dataset.url;
  fetch(apiUrl)
    .then((res) => res.json())
    .then((data) => {
      // topicName.textContent = data.topic.name;
      subtopicTitle.textContent = data.subtopic.title;

      exercises = data.exercises;

      // Chỉ thêm intro để sử dụng cho Full transcript, nhưng ko render bên Dictation
      exercises.unshift({
        is_intro: true,
        correct_text: data.subtopic.title,
        translation: "",
        timeStart: 0,
        timeEnd: 0,
        audioSrc: data.subtopic.full_audioSrc,
      });

      fullAudio.src = data.subtopic.full_audioSrc;

      // Khi bắt đầu Dictation thì bỏ qua Intro (index = 1)
      currentIndex = 1;

      exerciseTotal.textContent = exercises.length - 1; // Đúng số câu real
      slideTotal.textContent = exercises.length - 1;

      renderDictation();
      renderSlide();
      renderTranscript();

      prevBtn.onclick = () => {
        if (currentIndex > 1) currentIndex--;
        updateAll();
      }; // chỉnh > 1
      nextBtn.onclick = () => {
        if (currentIndex < exercises.length - 1) currentIndex++;
        updateAll();
      };
      slidePrev.onclick = prevBtn.onclick;
      slideNext.onclick = nextBtn.onclick;
    });

  function updateAll() {
    renderDictation();
    renderSlide();
    scrollToActiveTranscript();
  }

  function renderDictation() {
    const ex = exercises[currentIndex];
    exerciseIndex.textContent = currentIndex;

    if (ex.is_intro) {
      exerciseContent.innerHTML = `
          <div class="text-center mb-3">
              <h5 class="fw-bold">${ex.correct_text}</h5>
          </div>
          <audio controls class="w-50 mb-3">
              <source src="${ex.audioSrc}" type="audio/mp3">
          </audio>
          `;
    } else {
      exerciseContent.innerHTML = `
          <audio controls class="w-50 mb-3">
              <source src="${ex.audioSrc}" type="audio/mp3">
          </audio>
          <input type="text" id="user-answer" class="form-control mb-3 w-50" style="height: 60px; font-size: 20px;" placeholder="Type what you hear">
          <div id="answer-result" class="mt-2"></div>
          <div class="d-flex gap-2">
              <button class="btn btn-primary" id="check-answer-btn">Check</button>
              <button class="btn btn-outline-secondary" id="skip-btn">Skip</button>
          </div>
          `;

      // Thêm sự kiện Check
      document.getElementById("check-answer-btn").onclick = () => {
        const input = document.getElementById("user-answer");
        const userInput = input.value.trim().toLowerCase();
        const correctText = exercises[currentIndex].correct_text.trim();
        const correct = correctText.toLowerCase();
        const resultDiv = document.getElementById("answer-result");

        if (correct.startsWith(userInput) && userInput.length > 0) {
          input.classList.remove("is-invalid");
          input.classList.add("is-valid");
          resultDiv.innerHTML = `<span class="text-success fw-bold">Correct so far! ✅</span>`;
        } else {
          input.classList.remove("is-valid");
          input.classList.add("is-invalid");
          // Chỉ hiện phần đúng đến đâu
          const partial = correctText.split(" ").slice(0, 1).join(" ");
          resultDiv.innerHTML = `
                  <span class="text-danger fw-bold">Incorrect ❌</span><br>
                  <small class="text-muted">Correct answer: <strong>${partial}</strong></small>
                  `;
        }
      };

      document.getElementById("skip-btn").onclick = () => {
        if (currentIndex < exercises.length - 1) {
          currentIndex++;
          updateAll();
        }
      };
    }
  }

  function renderSlide() {
    const ex = exercises[currentIndex];
    slideIndex.textContent = currentIndex;
    slideText.textContent = ex.correct_text;
    slideTrans.textContent = ex.translation || "Bản dịch tiếng Việt";
  }

  function renderTranscript() {
    transcriptList.innerHTML = "";
    exercises.forEach((ex, idx) => {
      if (idx === 0) return;
      const li = document.createElement("li");
      li.classList.add("list-group-item");
      li.dataset.index = idx;
      li.innerHTML = `
          <div class="d-flex align-items-center mb-1">
            <button class="btn btn-sm btn-outline-primary me-2 play-btn">
              <i class="bi bi-play-fill"></i>
            </button>
            <strong>${ex.correct_text}</strong>
          </div>
          <small class="text-muted">${
            ex.translation || "Bản dịch tiếng Việt"
          }</small>
        `;
      const btn = li.querySelector(".play-btn");
      btn.onclick = () => {
        fullAudio.currentTime = ex.timeStart;
        fullAudio.play();
        currentIndex = idx;
        updateAll();
      };
      transcriptList.appendChild(li);
    });
  }

  function scrollToActiveTranscript() {
    if (currentIndex === 0) return;
    const el = transcriptList.children[currentIndex - 1];
    if (el && autoScroll.checked) {
      transcriptList.scrollTo({
        top:
          el.offsetTop - transcriptList.clientHeight / 2 + el.clientHeight / 2,
        behavior: "smooth",
      });
    }
  }

  fullAudio.ontimeupdate = () => {
    const currentTime = fullAudio.currentTime;
    exercises.forEach((ex, idx) => {
      if (idx === 0) return;
      const item = transcriptList.children[idx - 1];
      if (currentTime >= ex.timeStart && currentTime <= ex.timeEnd) {
        item.classList.add("active");
        if (currentIndex !== idx) {
          currentIndex = idx;
          renderSlide();
          exerciseIndex.textContent = idx;
          if (autoScroll.checked) scrollToActiveTranscript();
        }
      } else {
        item.classList.remove("active");
      }
    });
  };

  document.addEventListener("keydown", (e) => {
    if (e.code === "Space") {
      e.preventDefault();
      fullAudio.paused ? fullAudio.play() : fullAudio.pause();
    } else if (e.code === "ArrowLeft") {
      slidePrev.click();
    } else if (e.code === "ArrowRight") {
      slideNext.click();
    }
  });
});
