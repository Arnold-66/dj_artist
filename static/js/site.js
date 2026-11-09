(function () {
  "use strict";

  /* ---------- Umami config ---------- */
  var UMAMI_SRC = "https://cloud.umami.is/script.js";
  var UMAMI_WEBSITE_ID = "32d7397d-0f73-44c6-8f8a-b5e88b205b05";

  function loadUmami() {
    if (window._umamiLoaded) return;
    window._umamiLoaded = true;

    var script = document.createElement("script");
    script.defer = true;
    script.src = UMAMI_SRC;
    script.setAttribute("data-website-id", UMAMI_WEBSITE_ID);
    document.head.appendChild(script);
  }

  /* ---------- Cookie banner ---------- */
  var cookieKey = "dj-cookie-choice";
  var banner = document.getElementById("cookie-banner");
  if (banner && !localStorage.getItem(cookieKey)) banner.hidden = false;

  function saveCookieChoice(value) {
    try { localStorage.setItem(cookieKey, value); } catch (_) {}
    if (banner) banner.hidden = true;
  }

  var acceptBtn = document.getElementById("cookie-accept");
  var rejectBtn = document.getElementById("cookie-reject");

  if (acceptBtn) acceptBtn.addEventListener("click", function () {
    saveCookieChoice("accepted");
    loadUmami();
  });

  if (rejectBtn) rejectBtn.addEventListener("click", function () {
    saveCookieChoice("essential-only");
    // No analytics loaded
  });

  /* Returning visitor who already accepted → load Umami immediately */
  try {
    if (localStorage.getItem(cookieKey) === "accepted") loadUmami();
  } catch (_) {}


  /* ============================================================
     MEDIA PLAYER  (video + audio, uses native <video>/<audio>)
     ============================================================ */
  function initPlayer(player) {
    if (!player || player.dataset.initialized === "true") return;
    var media = player.querySelector(".media-player-native");
    if (!media) return;
    player.dataset.initialized = "true";

    var toggle = player.querySelector(".media-player-toggle");
    var playIcon = player.querySelector(".mp-icon-play");
    var pauseIcon = player.querySelector(".mp-icon-pause");
    var curEl = player.querySelector(".media-player-current");
    var durEl = player.querySelector(".media-player-duration");
    var seek = player.querySelector(".media-player-seek");
    var muteBtn = player.querySelector(".media-player-mute");
    var fsBtn = player.querySelector(".media-player-fullscreen");
    var errorBox = player.querySelector(".media-player-error");

    function showError(msg) {
      if (errorBox) { errorBox.textContent = msg; errorBox.hidden = false; }
      console.error("[player]", msg, media.currentSrc);
    }
    function clearError() { if (errorBox) errorBox.hidden = true; }

    function updatePlayButton() {
      var playing = !media.paused && !media.ended;
      if (playIcon) playIcon.hidden = playing;
      if (pauseIcon) pauseIcon.hidden = !playing;
      player.classList.toggle("is-playing", playing);
      if (toggle) toggle.setAttribute("aria-label", playing ? "Pause" : "Play");
    }

    function updateProgress() {
      if (!Number.isFinite(media.duration) || media.duration <= 0) return;
      var pct = (media.currentTime / media.duration) * 100;
      if (seek) seek.value = pct;
      if (curEl) curEl.textContent = formatTime(media.currentTime);
      if (durEl) durEl.textContent = formatTime(media.duration);
    }

    async function togglePlayback() {
      clearError();
      if (media.paused || media.ended) {
        try { await media.play(); }
        catch (err) { showError("Playback failed. Check the file format and server response."); }
      } else {
        media.pause();
      }
    }

    if (toggle) toggle.addEventListener("click", togglePlayback);

    media.addEventListener("play", updatePlayButton);
    media.addEventListener("pause", updatePlayButton);
    media.addEventListener("ended", updatePlayButton);
    media.addEventListener("timeupdate", updateProgress);
    media.addEventListener("loadedmetadata", function () { clearError(); updateProgress(); });
    media.addEventListener("durationchange", updateProgress);
    media.addEventListener("canplay", clearError);
    media.addEventListener("error", function () {
      var code = media.error ? media.error.code : 0;
      var msg = "Unable to load this media file.";
      if (code === 1) msg = "Media playback was interrupted.";
      else if (code === 2) msg = "Network error while loading the media.";
      else if (code === 3) msg = "The media file could not be decoded.";
      else if (code === 4) msg = "Unsupported media format or missing file.";
      showError(msg);
    });
    media.addEventListener("stalled", function () { console.warn("[player] stalled:", media.currentSrc); });

    if (seek) {
      seek.addEventListener("input", function () {
        if (Number.isFinite(media.duration) && media.duration > 0) {
          media.currentTime = (Number(seek.value) / 100) * media.duration;
        }
      });
    }

    if (muteBtn) {
      muteBtn.addEventListener("click", function () {
        media.muted = !media.muted;
        muteBtn.innerHTML = media.muted
          ? '<i class="fa-solid fa-volume-xmark"></i>'
          : '<i class="fa-solid fa-volume-high"></i>';
        muteBtn.setAttribute("aria-label", media.muted ? "Unmute" : "Mute");
      });
    }

    if (fsBtn) {
      fsBtn.addEventListener("click", async function () {
        try {
          if (media.requestFullscreen) await media.requestFullscreen();
          else if (media.webkitEnterFullscreen) media.webkitEnterFullscreen();
        } catch (err) { console.error("[player] fullscreen:", err); }
      });
    }

    try { media.load(); } catch (_) {}
    updatePlayButton();
  }

  function initAllPlayers() {
    document.querySelectorAll(".media-player").forEach(initPlayer);
  }

  /* ============================================================
     DS-PLAYER  (compact custom audio — .ds-player)
     THIS is what was missing. It wires the gold progress line.
     ============================================================ */
  function initDsPlayer(root) {
    if (!root || root.dataset.dsInitialized === "true") return;
    var audio = root.querySelector("audio");
    if (!audio) return;
    root.dataset.dsInitialized = "true";

    var btn       = root.querySelector(".ds-btn");
    var progress  = root.querySelector(".ds-progress");
    var fill      = root.querySelector(".ds-progress-fill");
    var timeEl    = root.querySelector(".ds-time");
    var volume    = root.querySelector(".ds-volume");

    /* Play / Pause */
    if (btn) {
      btn.addEventListener("click", function () {
        if (audio.paused) audio.play().catch(function () {});
        else audio.pause();
      });
    }

    function updateIcon() {
      if (!btn) return;
      btn.innerHTML = audio.paused
        ? '<i class="fa-solid fa-play"></i>'
        : '<i class="fa-solid fa-pause"></i>';
    }

    audio.addEventListener("play",  updateIcon);
    audio.addEventListener("pause", updateIcon);
    audio.addEventListener("ended", updateIcon);

    /* Gold progress fill — the fix */
    function updateProgress() {
      var d = audio.duration;
      var c = audio.currentTime;
      if (Number.isFinite(d) && d > 0 && fill) {
        fill.style.width = ((c / d) * 100) + "%";
        if (timeEl) timeEl.textContent = formatTime(c) + " / " + formatTime(d);
      } else if (timeEl) {
        timeEl.textContent = formatTime(c);
      }
    }

    audio.addEventListener("timeupdate", updateProgress);
    audio.addEventListener("loadedmetadata", updateProgress);
    audio.addEventListener("durationchange", updateProgress);
    audio.addEventListener("seeked", updateProgress);

    /* Click-to-seek on the progress bar */
    if (progress) {
      progress.addEventListener("click", function (e) {
        var rect = progress.getBoundingClientRect();
        var pct  = (e.clientX - rect.left) / rect.width;
        if (Number.isFinite(audio.duration) && audio.duration > 0) {
          audio.currentTime = Math.max(0, Math.min(1, pct)) * audio.duration;
          updateProgress();
        }
      });
    }

    /* Volume */
    if (volume) {
      volume.addEventListener("input", function () {
        var v = parseFloat(volume.value);
        if (Number.isFinite(v)) audio.volume = v;
      });
    }

    updateIcon();
  }

  function initAllDsPlayers() {
    document.querySelectorAll(".ds-player").forEach(initDsPlayer);
  }

  /* ============================================================
     BOOT
     ============================================================ */
  function initAll() {
    initAllPlayers();
    initAllDsPlayers();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }

  /* Support players added later (AJAX, admin live views, etc.) */
  if (window.MutationObserver) {
    var observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        m.addedNodes.forEach(function (node) {
          if (node.nodeType !== 1) return;

          if (node.matches && node.matches(".media-player")) initPlayer(node);
          if (node.matches && node.matches(".ds-player")) initDsPlayer(node);

          if (node.querySelectorAll) {
            node.querySelectorAll(".media-player").forEach(initPlayer);
            node.querySelectorAll(".ds-player").forEach(initDsPlayer);
          }
        });
      });
    });
    var startObserver = function () {
      if (document.body) observer.observe(document.body, { childList: true, subtree: true });
    };
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", startObserver);
    } else {
      startObserver();
    }
  }
})();