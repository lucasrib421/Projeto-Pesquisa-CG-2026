#include "main-window.h"

#include <QtCore/QCommandLineParser>
#include <QtCore/QTimer>
#include <QtGui/QScreen>

int main(int argc, char *argv[])
{
	QApplication app(argc, argv);
	//srand(time(NULL));

	// Batch mode: generate one figure of the paper, or run the river experiment, then quit.
	QCommandLineParser parser;
	parser.addHelpOption();
	QCommandLineOption figureOption("figure", "Generate figure <n> of the paper and quit (supported: 11).", "n");
	QCommandLineOption experimentOption("experiment", "Run the river experiment and quit: baseline, control, reserve, passive or channel.", "mode");
	QCommandLineOption riverOption("river", "River CSV for --experiment: x,y in meters, elevation normalized to [0,1], from mouth to source.", "file");
	QCommandLineOption seedOption("seed", "Random seed for --experiment (default: 239, as the original code).", "n", "239");
	QCommandLineOption delayOption("spread-delay", "For --experiment channel: height levels before a river node spreads the growth (default: -1 = never).", "levels", "-1");
	QCommandLineOption outOption("out", "Output folder (default: Figures/).", "folder", "Figures/");
	QCommandLineOption stayOption("stay", "Keep the window open after --figure or --experiment.");
	parser.addOptions({ figureOption, experimentOption, riverOption, seedOption, delayOption, outOption, stayOption });
	parser.process(app);

	const bool figure = parser.isSet(figureOption);
	const bool experiment = parser.isSet(experimentOption);
	QString outFolder = parser.value(outOption);
	if (!outFolder.endsWith('/'))
		outFolder += '/';
	if (figure && experiment)
	{
		qCritical() << "Use either --figure or --experiment, not both";
		return 2;
	}
	if (figure && parser.value(figureOption) != "11")
	{
		qCritical() << "Unsupported figure:" << parser.value(figureOption) << "(supported: 11)";
		return 2;
	}
	bool seedOk;
	const int seed = parser.value(seedOption).toInt(&seedOk);
	if (!seedOk)
	{
		qCritical() << "Invalid seed:" << parser.value(seedOption);
		return 2;
	}
	bool delayOk;
	const double spreadDelay = parser.value(delayOption).toDouble(&delayOk);
	if (!delayOk)
	{
		qCritical() << "Invalid spread delay:" << parser.value(delayOption);
		return 2;
	}
	const bool stay = parser.isSet(stayOption);

	MainWindow mainWin;

    // Open on the second screen if there is one, otherwise the main screen.
    const QList<QScreen*> screens = QGuiApplication::screens();
    QScreen* targetScreen = (screens.size() > 1) ? screens.at(1) : QGuiApplication::primaryScreen();

    mainWin.move(targetScreen->availableGeometry().topLeft());
    mainWin.showMaximized();

	int exitCode = 0;
	if (figure || experiment)
	{
		// Runs once the event loop has started, so the OpenGL widget is initialized.
		QTimer::singleShot(0, &mainWin, [&]() {
			if (figure)
			{
				mainWin.GenerateFigure11(outFolder);
				qInfo() << "Figure 11 written to" << outFolder;
			}
			else if (mainWin.RunRiverExperiment(parser.value(experimentOption), parser.value(riverOption), seed, outFolder, spreadDelay))
				qInfo() << "Experiment written to" << outFolder;
			else
				exitCode = 1;

			if (!stay || exitCode != 0)
				app.exit(exitCode);
		});
	}
	const int loopCode = app.exec();
	return exitCode != 0 ? exitCode : loopCode;
}
