import random
import time

from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from texts import PASSAGES

BG = "#1e1e2e"
SURFACE = "#313244"
TEXT = "#cdd6f4"
SUBTEXT = "#6c7086"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"
BLUE = "#89b4fa"


class TypingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._passage = ""
        self._start_time: float | None = None
        self._elapsed = 0.0
        self._finished = False

        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._tick)

        self._build_ui()
        self._load_passage()
        # re-render after layout is finalised so text width is known
        self._passage_label.viewport().installEventFilter(self)

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG}; color: {TEXT};")

        mono = QFont("Consolas", 14)
        mono.setStyleHint(QFont.StyleHint.Monospace)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Typing Speed Test")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 22, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {BLUE};")
        layout.addWidget(title)

        # Passage display — QTextBrowser wraps HTML rich text correctly
        self._passage_label = QTextBrowser()
        self._passage_label.setFont(mono)
        self._passage_label.setReadOnly(True)
        self._passage_label.setOpenLinks(False)
        # FixedPixelWidth is the only mode that reliably constrains HTML text width in Qt
        self._passage_label.setLineWrapMode(QTextBrowser.LineWrapMode.FixedPixelWidth)
        self._passage_label.setLineWrapColumnOrWidth(620)
        self._passage_label.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._passage_label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._passage_label.setStyleSheet(
            f"background-color: {SURFACE}; color: {TEXT}; "
            "border-radius: 8px; padding: 16px; border: none;"
        )
        self._passage_label.setMinimumHeight(140)
        self._passage_label.setFixedHeight(200)
        self._passage_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self._passage_label)

        # Input box
        self._input = QTextEdit()
        self._input.setFont(mono)
        self._input.setFixedHeight(60)
        self._input.setPlaceholderText("Start typing here…")
        self._input.setStyleSheet(
            f"background-color: {SURFACE}; color: {TEXT}; "
            f"border: 2px solid {SUBTEXT}; border-radius: 8px; padding: 8px;"
        )
        self._input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._input)

        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(40)

        self._wpm_label = self._stat_label("WPM", "--")
        self._acc_label = self._stat_label("Accuracy", "--%")
        self._time_label = self._stat_label("Time", "0s")

        stats_layout.addStretch()
        for w in (self._wpm_label, self._acc_label, self._time_label):
            stats_layout.addWidget(w)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # Restart button
        self._restart_btn = QPushButton("Restart")
        self._restart_btn.setFixedWidth(140)
        self._restart_btn.setFixedHeight(40)
        self._restart_btn.setFont(QFont("Segoe UI", 12))
        self._restart_btn.setStyleSheet(
            f"background-color: {BLUE}; color: {BG}; border-radius: 8px; font-weight: bold;"
            f"QPushButton:hover {{ background-color: {GREEN}; }}"
        )
        self._restart_btn.clicked.connect(self._restart)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self._restart_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _stat_label(self, heading: str, value: str) -> QLabel:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(2)

        h = QLabel(heading)
        h.setFont(QFont("Segoe UI", 9))
        h.setStyleSheet(f"color: {SUBTEXT};")
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)

        v = QLabel(value)
        v.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        v.setStyleSheet(f"color: {YELLOW};")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox.addWidget(h)
        vbox.addWidget(v)

        # Store reference on the container so callers can update it
        container._value_label = v  # type: ignore[attr-defined]
        return container

    def eventFilter(self, obj, event):
        if obj is self._passage_label.viewport() and event.type() == QEvent.Type.Resize:
            self._render_passage(self._input.toPlainText())
        return super().eventFilter(obj, event)

    def _load_passage(self):
        self._passage = random.choice(PASSAGES)
        self._render_passage("")

    def _render_passage(self, typed: str):
        parts = []
        for i, ch in enumerate(self._passage):
            escaped = ch.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if i < len(typed):
                color = GREEN if typed[i] == ch else RED
                parts.append(f'<span style="color:{color};">{escaped}</span>')
            else:
                parts.append(f'<span style="color:{SUBTEXT};">{escaped}</span>')
        self._passage_label.setHtml(
            f'<p style="font-family:Consolas,monospace; font-size:14pt; margin:0;">{"".join(parts)}</p>'
        )

    def _on_text_changed(self):
        if self._finished:
            return

        typed = self._input.toPlainText()

        # Prevent typing beyond the passage length
        if len(typed) > len(self._passage):
            cursor = self._input.textCursor()
            self._input.blockSignals(True)
            self._input.setPlainText(typed[: len(self._passage)])
            cursor.movePosition(cursor.MoveOperation.End)
            self._input.setTextCursor(cursor)
            self._input.blockSignals(False)
            typed = typed[: len(self._passage)]

        # Start timer on first character
        if typed and self._start_time is None:
            self._start_time = time.monotonic()
            self._timer.start()

        self._render_passage(typed)
        self._update_stats(typed)

        if len(typed) == len(self._passage):
            self._finish()

    def _tick(self):
        if self._start_time is not None:
            self._elapsed = time.monotonic() - self._start_time
            self._time_label._value_label.setText(f"{self._elapsed:.1f}s")  # type: ignore[attr-defined]

    def _update_stats(self, typed: str):
        if not typed or self._start_time is None:
            return

        elapsed = time.monotonic() - self._start_time
        correct = sum(1 for i, ch in enumerate(typed) if i < len(self._passage) and ch == self._passage[i])
        total = len(typed)

        wpm = (correct / 5) / (elapsed / 60) if elapsed > 0 else 0
        accuracy = (correct / total * 100) if total > 0 else 100

        self._wpm_label._value_label.setText(f"{wpm:.0f}")  # type: ignore[attr-defined]
        self._acc_label._value_label.setText(f"{accuracy:.0f}%")  # type: ignore[attr-defined]

    def _finish(self):
        self._finished = True
        self._timer.stop()
        self._input.setReadOnly(True)
        self._input.setStyleSheet(
            f"background-color: {SURFACE}; color: {SUBTEXT}; "
            f"border: 2px solid {GREEN}; border-radius: 8px; padding: 8px;"
        )

    def _restart(self):
        self._timer.stop()
        self._start_time = None
        self._elapsed = 0.0
        self._finished = False

        self._input.blockSignals(True)
        self._input.setReadOnly(False)
        self._input.clear()
        self._input.setStyleSheet(
            f"background-color: {SURFACE}; color: {TEXT}; "
            f"border: 2px solid {SUBTEXT}; border-radius: 8px; padding: 8px;"
        )
        self._input.blockSignals(False)

        self._wpm_label._value_label.setText("--")  # type: ignore[attr-defined]
        self._acc_label._value_label.setText("--%")  # type: ignore[attr-defined]
        self._time_label._value_label.setText("0s")  # type: ignore[attr-defined]

        self._load_passage()
        self._input.setFocus()


class TypingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Typing Speed Test")
        self.setMinimumSize(720, 520)
        self.resize(780, 560)
        self.setCentralWidget(TypingWidget())
