#include "main-window.h"

#include <QtCore/QCommandLineParser>
#include <QtCore/QTimer>
#include <QtGui/QScreen>

int main(int argc, char *argv[])
{
	QApplication app(argc, argv);
	//srand(time(NULL));

	// Batch mode: generate one figure of the paper, then quit.
	QCommandLineParser parser;
	parser.addHelpOption();
	QCommandLineOption figureOption("figure", "Generate figure <n> of the paper and quit (supported: 11).", "n");
	QCommandLineOption outOption("out", "Output folder for --figure (default: Figures/).", "folder", "Figures/");
	parser.addOption(figureOption);
	parser.addOption(outOption);
	parser.process(app);

	const bool batch = parser.isSet(figureOption);
	QString outFolder = parser.value(outOption);
	if (!outFolder.endsWith('/'))
		outFolder += '/';
	if (batch && parser.value(figureOption) != "11")
	{
		qCritical() << "Unsupported figure:" << parser.value(figureOption) << "(supported: 11)";
		return 2;
	}

	MainWindow mainWin;

    // Open on the second screen if there is one, otherwise the main screen.
    const QList<QScreen*> screens = QGuiApplication::screens();
    QScreen* targetScreen = (screens.size() > 1) ? screens.at(1) : QGuiApplication::primaryScreen();

    mainWin.move(targetScreen->availableGeometry().topLeft());
    mainWin.showMaximized();

	if (batch)
	{
		// Runs once the event loop has started, so the OpenGL widget is initialized.
		QTimer::singleShot(0, &mainWin, [&]() {
			mainWin.GenerateFigure11(outFolder);
			qInfo() << "Figure 11 written to" << outFolder;
			app.quit();
		});
	}
	return app.exec();
}
