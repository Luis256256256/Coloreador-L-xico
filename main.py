from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit,
    QMenuBar, QMenu, QFileDialog, QStatusBar
)
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QAction
from PySide6.QtCore import Qt, QRegularExpression
import sys
import re




class PHPHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.lexeme_stats = {
            "keyword": {}, "operator": {}, "literal": {},
            "comment": {}, "delimiter": {}, "identifier": {}, "unrecognized": {}
        }


        self.recognized_lexemes = set()

        self.rules = [
            (r"\$[a-zA-Z_]\w*|\b[a-zA-Z_]\w*\b", "identifier", QColor("#9cdcfe")),
            (r"\b(echo|function|return|if|else|while|for|foreach|switch|case|break|continue|default|class|public|private|protected|static|new|try|catch|finally|throw)\b", "keyword", QColor("#007acc")),
            (r"//.*|#.*|/\*[\s\S]*?\*/", "comment", QColor("#6a9955")),
            (r'"[^"]*"|\'[^\']*\'|\b\d+\b', "literal", QColor("#ce9178")),
            (r"[\+\-\*/=<>!&|\.]{1,2}", "operator", QColor("#d4d4d4")),
            (r"[()\[\]{};:,]", "delimiter", QColor("#d4d4d4")),
            
        ]

    def highlightBlock(self, text):
        self.recognized_lexemes.clear()
        for pattern, category, color in self.rules:
            regex = QRegularExpression(pattern)
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            match_iter = regex.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                lexeme = match.captured()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
                self._count_lexeme(lexeme, category)
                self._count_lexeme(lexeme, category)
                self.recognized_lexemes.add(lexeme)

        self._detect_unrecognized_lexemes(text)
        

    def _count_lexeme(self, lexeme, category):
        lexeme = lexeme.strip()
        if lexeme:
            stats = self.lexeme_stats[category]
            stats[lexeme] = stats.get(lexeme, 0) + 1

    def get_lexeme_stats(self):
        return {
            category: dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
            for category, stats in self.lexeme_stats.items()
        }

    def _detect_unrecognized_lexemes(self, text):
        tokens = re.findall(r"\S+", text)
        for token in tokens:
            if token not in self.recognized_lexemes:
                self._count_lexeme(token, "unrecognized")
                self._handle_unrecognized(token)

    def _handle_unrecognized(self, lexeme):
        print('lexema no reconocido')

    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor php")
        self.editor = QPlainTextEdit()
        self.setCentralWidget(self.editor)
        self.highlighter = PHPHighlighter(self.editor.document())
        self.create_menu()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.editor.textChanged.connect(self.on_text_changed)



    

    def on_text_changed(self):
        stats = self.highlighter.get_lexeme_stats()
        self.update_status_bar(stats)


    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Opciones")

        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        open_action = QAction("Mostrar estadisticas", self)
        open_action.triggered.connect(self.show_stats)
        file_menu.addAction(open_action)

        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def update_status_bar(self, lexeme_stats):
        total = sum(len(lexemes) for lexemes in lexeme_stats.values())
        print(lexeme_stats)
        unrecognized = lexeme_stats.get("unrecognized", {})
        if unrecognized:
            self.status_bar.setStyleSheet("color: red;")
            self.status_bar.showMessage(f"No valido")
        else:
            self.status_bar.setStyleSheet("color: green;")
            self.status_bar.showMessage(f"Valido")

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "", "Scripts php (*.php)")
        if file_name:
            with open(file_name, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Scripts php (*.php)")
        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())

    def show_stats(self):
        stats = self.highlighter.get_lexeme_stats()
        for category, lexemes in stats.items():
            print(f"\n{category.upper()}:")
            for lex, count in lexemes.items():
                print(f"  {lex}: {count}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
