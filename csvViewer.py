
import sys, os
import numpy as np
import pandas as pd

from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
from PySide6.QtCore import Slot, QUrl, Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

import plotly.graph_objs as go
import plotly.offline

class MainWindow(QMainWindow):
    def __init__(self, argv):
        super().__init__()
        self.button = QPushButton("Open File")
        self.button.clicked.connect(self.open_files)
        self.setCentralWidget(self.button)
        self.df = []
        self.web = []
        if len(argv) > 1:
            self.tag = argv[1:]
        else:
            self.tag = []
        self.setWindowTitle(f'Tag = {self.tag}')
        if not Path('fig').exists():
            Path('fig').mkdir(parents=True, exist_ok=True)
        # print(self.tag, len(self.tag))

    def open_files(self, checked):
        filenames = QFileDialog.getOpenFileNames()[0]
        count = 0
        self.df = []
        for k in range(len(filenames)):
            ext = filenames[k].split('.')[-1].lower()
            if ext == 'csv':
                count += 1
                print(f'[{count:3d}] {filenames[k]}')
                df = pd.read_csv(filenames[k])
                self.df.append(df)

                filename = filenames[k].split('/')[-1].split('.')[0]

                fig = go.Figure()
                nsample = range(df.shape[0])
                if len(self.tag) > 0:
                    for i in range(len(self.tag)):
                        tag = self.tag[i]
                        if tag == 'an':
                            df.loc[:, 'an'] = np.sqrt(np.sum(df.loc[:, ['ax','ay','az']].to_numpy()**2, axis=1))
                        elif tag == 'gn':
                            df.loc[:, 'gn'] = np.sqrt(np.sum(df.loc[:, ['gx','gy','gz']].to_numpy()**2, axis=1))
                        elif tag == 'mn':
                            df.loc[:, 'mn'] = np.sqrt(np.sum(df.loc[:, ['mx','my','mz']].to_numpy()**2, axis=1))
                        fig.add_trace(go.Scatter(
                            x=list(nsample),
                            y=df.loc[:, tag],
                            name=f'{tag}'
                        ))

                fig.update_layout(title_text=f'[{count}] {filename}', hovermode='x unified')
                web = self.plot_qt(fig, filename)
                web.show()
                self.web.append(web)

    def plot_qt(self, fig, name):
        plotly.offline.plot(fig, filename=f'fig/{name}.html', auto_open=False)
        web = QWebEngineView()
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f'fig/{name}.html'))
        web.load(QUrl.fromLocalFile(file_path))
        web.resize(1200, 500)
        web.setWindowTitle(name)
        return web

def main():
    app = QApplication(sys.argv)
    # app.setStyleSheet('QMainWindow{background-color: darkgray;border: 1px solid black;}')
    w = MainWindow(sys.argv)
    # w.setWindowFlags(Qt.FramelessWindowHint)
    w.resize(500, 50)
    w.show()
    app.exec()

if __name__ == "__main__":
    main()
