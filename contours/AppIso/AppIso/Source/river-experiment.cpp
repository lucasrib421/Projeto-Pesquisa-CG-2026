#include "main-window.h"
#include "river-generation.h"

#include <QtCore/QDir>
#include <QtCore/QElapsedTimer>
#include <QtCore/QFile>
#include <QtCore/QTextStream>

#include <cmath>

namespace
{
	struct RiverPoint
	{
		Vector2 p;
		double elevation;
	};

	struct RiverNode
	{
		int node;
		double elevation; // requested elevation, interpolated along the polyline
	};

	// Reads "x,y,elevation" lines (meters), from the mouth to the source.
	// Empty lines, lines starting with '#' and non-numeric lines (header) are skipped.
	QVector<RiverPoint> ReadRiverCsv(const QString& file)
	{
		QVector<RiverPoint> river;
		QFile f(file);
		if (!f.open(QIODevice::ReadOnly | QIODevice::Text))
			return river;

		QTextStream in(&f);
		while (!in.atEnd())
		{
			QString line = in.readLine().trimmed();
			if (line.isEmpty() || line.startsWith('#'))
				continue;
			QStringList cols = line.split(',');
			if (cols.size() < 3)
				continue;
			bool okx, oky, oke;
			double x = cols[0].toDouble(&okx), y = cols[1].toDouble(&oky), e = cols[2].toDouble(&oke);
			if (okx && oky && oke)
				river.append({ Vector2(x, y), e });
		}
		return river;
	}

	// Decision D2: a river must not go up from mouth to source. Running maximum; returns the number of corrected points.
	int MakeMonotonic(QVector<RiverPoint>& river)
	{
		int corrected = 0;
		for (int k = 1; k < river.size(); ++k)
		{
			if (river[k].elevation < river[k - 1].elevation)
			{
				river[k].elevation = river[k - 1].elevation;
				++corrected;
			}
		}
		return corrected;
	}

	int NearestNode(const GraphPoisson& g, const Vector2& q)
	{
		int best = -1;
		double bestDist = Math::Infinity;
		for (int i = 0; i < g.Size(); ++i)
		{
			double d = SquaredNorm(g.Position(i) - q);
			if (d < bestDist)
			{
				bestDist = d;
				best = i;
			}
		}
		return best;
	}

	// Decision D4: walk the polyline with a step of r/4 and keep the nearest graph node at each step, without repetition.
	QVector<RiverNode> MapRiverToGraph(const GraphPoisson& g, const QVector<RiverPoint>& river)
	{
		QVector<RiverNode> nodes;
		QSet<int> used;
		auto add = [&](const Vector2& q, double e) {
			int n = NearestNode(g, q);
			if (n != -1 && !used.contains(n))
			{
				used.insert(n);
				nodes.append({ n, e });
			}
		};

		if (river.size() == 1)
			add(river[0].p, river[0].elevation);

		double step = g.Radius() / 4;
		for (int k = 0; k + 1 < river.size(); ++k)
		{
			Vector2 a = river[k].p, b = river[k + 1].p;
			int n = Math::Max(1, int(std::ceil(Norm(b - a) / step)));
			for (int s = 0; s <= n; ++s)
			{
				double t = double(s) / n;
				add(a + t * (b - a), river[k].elevation + t * (river[k + 1].elevation - river[k].elevation));
			}
		}
		return nodes;
	}

	// Number of consecutive river nodes that are not neighbours in the graph (a gap breaks the no-pit argument)
	int CountGaps(const GraphPoisson& g, const QVector<RiverNode>& nodes)
	{
		int gaps = 0;
		for (int k = 0; k + 1 < nodes.size(); ++k)
		{
			if (!g.Neighbours(nodes[k].node).contains(nodes[k + 1].node))
				++gaps;
		}
		return gaps;
	}
}

/*
 * River experiment, same setup as GenerateFigure11 (mask, histogram, ~3000 particles).
 *
 * \param mode "baseline": river drawn in the probability map P (Figure 11), no seeds;
 *             "control": uniform P, no seeds (isolates the effect of the river);
 *             "reserve" / "passive": uniform P and the river of riverFile as seeds (decision D1 A / B);
 *             "channel": as "reserve", but the growth does not spread from the river (incised riverbed)
 * \param riverFile CSV "x,y,elevation" from mouth to source. For the baseline it is only used to measure.
 * \param seed Seed of the random generators (239 = default of the original code)
 * \param prefix Output folder
 * \param spreadDelayLevels "channel" only: delay before a river node spreads the growth, in height levels
 *        (one level = number of nodes / number of histogram bins ranks); negative = never
 */
bool MainWindow::RunRiverExperiment(const QString& mode, const QString& riverFile, int seed, const QString& prefix, double spreadDelayLevels)
{
	IsoVectoGenerationRiver::Mode genMode;
	const bool riverInP = (mode == "baseline");
	if (mode == "baseline" || mode == "control")
		genMode = IsoVectoGenerationRiver::Mode::None;
	else if (mode == "reserve")
		genMode = IsoVectoGenerationRiver::Mode::Reserve;
	else if (mode == "passive")
		genMode = IsoVectoGenerationRiver::Mode::Passive;
	else if (mode == "channel")
		genMode = IsoVectoGenerationRiver::Mode::Channel;
	else
	{
		qCritical() << "[River] Unknown mode" << mode << "(baseline, control, reserve, passive, channel)";
		return false;
	}

	QVector<RiverPoint> river;
	if (!riverFile.isEmpty())
	{
		river = ReadRiverCsv(riverFile);
		if (river.isEmpty())
		{
			qCritical() << "[River] No point read from" << riverFile;
			return false;
		}
	}
	else if (genMode != IsoVectoGenerationRiver::Mode::None)
	{
		qCritical() << "[River] Mode" << mode << "needs --river <file.csv>";
		return false;
	}
	int corrected = MakeMonotonic(river);

	QDir().mkpath(prefix);

	// Same inputs and call order as GenerateFigure11, so that "baseline" with seed 239 reproduces it
	Random::R239 = Random(seed);
	ChangeBoxes(Box2(500));
	ChangeMaskFromFile("../Images/input/mask.png");
	ChangeHistogramFromFile("../Data/dems/rockies_zoom_breach.png", 12);
	ChangeEstimatedNbParticles(3000);
	if (riverInP)
		ChangeNoiseFromFile("../Images/input/proba.png", 4);
	else
		ChangeNoise(ScalarField2(Box2(0.5), 256, 256, 1));

	QElapsedTimer timer;
	timer.start();
	CreateGenerationZones();
	qint64 msGraph = timer.elapsed();
	const GraphPoisson& g = m_generation_graph_zones;
	const int n = g.Size();

	// River nodes and target ranks (start of the histogram bin nearest to the requested elevation)
	QVector<RiverNode> riverNodes = MapRiverToGraph(g, river);
	int gaps = CountGaps(g, riverNodes);

	Histogram h = m_generation_histogram.ToHistogram(n);
	QVector<int> binStart;
	int count = 0;
	for (int i = 0; i < h.GetSize(); ++i)
	{
		binStart.append(count);
		count += h.Value(i);
	}
	auto nearestBin = [&](double e) {
		int best = -1;
		double bestDist = Math::Infinity;
		for (int i = 0; i < h.GetSize(); ++i)
		{
			double d = std::fabs(m_generation_histogram.GetKey(i) - e);
			if (h.Value(i) > 0 && d < bestDist)
			{
				bestDist = d;
				best = i;
			}
		}
		return best;
	};

	QVector<IsoVectoGenerationRiver::Seed> seeds;
	for (const RiverNode& rn : riverNodes)
		seeds.append({ rn.node, binStart[nearestBin(rn.elevation)] });

	// Growth
	timer.restart();
	IsoVectoGenerationRiver gen(g, m_generation_noise, genMode, seeds, seed);
	const int spreadDelayRanks = spreadDelayLevels < 0 ? -1 : int(std::lround(spreadDelayLevels * n / h.GetSize()));
	gen.SetSpreadDelay(spreadDelayRanks);
	gen.Generate();
	qint64 msGrowth = timer.elapsed();
	IsoVectoGenerationRiver::Stats stats = gen.GetStats();

	m_generation_graph_result = gen.Result();
	m_generation_graph_proba = gen.Proba();
	timer.restart();
	SetIsosFromHistogram();
	qint64 msIsos = timer.elapsed();

	// Images
	ExportIsosSVG(prefix + "isos.svg");
	ExportIsosInterpolate(prefix + "terrain.png", 512, 512);
	ExportNoise(prefix + "proba.png");

	// Graph data for the metrics (scripts/metrics.py)
	QHash<int, int> riverIndex;
	QHash<int, double> riverElevation;
	for (int k = 0; k < riverNodes.size(); ++k)
	{
		riverIndex[riverNodes[k].node] = k;
		riverElevation[riverNodes[k].node] = riverNodes[k].elevation;
	}

	QFile nodesFile(prefix + "nodes.csv");
	if (nodesFile.open(QIODevice::WriteOnly | QIODevice::Text))
	{
		QTextStream out(&nodesFile);
		out << "id,x,y,p,coast,river_index,target_elevation,rank,height\n";
		for (int i = 0; i < n; ++i)
		{
			Vector2 p = g.Position(i);
			out << i << ',' << p[0] << ',' << p[1] << ',' << m_generation_graph_proba[i] << ','
				<< (g.IsBorder(i) ? 1 : 0) << ',' << riverIndex.value(i, -1) << ','
				<< (riverIndex.contains(i) ? QString::number(riverElevation[i]) : QString()) << ','
				<< m_generation_graph_result[i] << ',' << m_generation_graph_heights[i] << '\n';
		}
	}

	QFile edgesFile(prefix + "edges.csv");
	if (edgesFile.open(QIODevice::WriteOnly | QIODevice::Text))
	{
		QTextStream out(&edgesFile);
		out << "a,b\n";
		for (int i = 0; i < n; ++i)
		{
			for (int j : g.Neighbours(i))
			{
				if (i < j)
					out << i << ',' << j << '\n';
			}
		}
	}

	QFile infoFile(prefix + "run_info.txt");
	if (infoFile.open(QIODevice::WriteOnly | QIODevice::Text))
	{
		QTextStream out(&infoFile);
		out << "mode=" << mode << '\n'
			<< "seed=" << seed << '\n'
			<< "spread_delay_levels=" << spreadDelayLevels << '\n'
			<< "spread_delay_ranks=" << spreadDelayRanks << '\n'
			<< "river_file=" << riverFile << '\n'
			<< "nodes=" << n << '\n'
			<< "poisson_radius=" << g.Radius() << '\n'
			<< "river_points=" << river.size() << '\n'
			<< "river_points_raised_D2=" << corrected << '\n'
			<< "river_nodes=" << riverNodes.size() << '\n'
			<< "river_gaps_D4=" << gaps << '\n'
			<< "seeds_activated_on_target=" << stats.activatedOnTarget << '\n'
			<< "seeds_already_assigned=" << stats.alreadyAssigned << '\n'
			<< "seeds_forced_early=" << stats.forcedEarly << '\n'
			<< "ms_graph=" << msGraph << '\n'
			<< "ms_growth=" << msGrowth << '\n'
			<< "ms_isolines=" << msIsos << '\n';
		out << "histogram_keys=";
		for (int i = 0; i < h.GetSize(); ++i)
			out << (i ? ";" : "") << m_generation_histogram.GetKey(i);
		out << "\nhistogram_counts=";
		for (int i = 0; i < h.GetSize(); ++i)
			out << (i ? ";" : "") << h.Value(i);
		out << '\n';
	}

	qInfo() << "[River]" << mode << "seed" << seed << ":" << riverNodes.size() << "river nodes," << gaps << "gaps,"
		<< stats.activatedOnTarget << "on target," << stats.alreadyAssigned << "already assigned," << stats.forcedEarly << "forced";
	return true;
}
