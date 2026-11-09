#include "river-generation.h"

#include <algorithm>

#define INITIAL_VALUE Math::Infinity
#define RESERVED_VALUE -1.0 // ranks are >= 0

/*
 * \param z The graph of the region
 * \param p The probability map, in [0, 1]
 * \param mode How river nodes interact with the natural growth
 * \param riverSeeds River nodes and their target ranks
 * \param seed Seed of the neighbour generator (239 reproduces IsoVectoGenerationV1)
 */
IsoVectoGenerationRiver::IsoVectoGenerationRiver(const GraphPoisson& z, const ScalarField2& p, Mode mode, const QVector<Seed>& riverSeeds, int seed)
	: IsoVectoGenerationV1(z, p), mode(mode), seeds(riverSeeds), rNeighbour(seed), rBorder(Random::R239)
{
	if (mode == Mode::None)
		seeds.clear();

	// Downstream nodes first when two targets are equal
	std::stable_sort(seeds.begin(), seeds.end(), [](const Seed& a, const Seed& b) { return a.targetRank < b.targetRank; });
}

void IsoVectoGenerationRiver::Generate()
{
	PreProcessRiver();

	while (nbAssigned != R.Size())
	{
		ActivateSeedsOnTarget();
		if (nbAssigned == R.Size())
			break;

		if (!GrowOneNode())
		{
			// Empty front: only possible while river nodes are still reserved
			if (!ForceNextSeed())
			{
				qWarning() << "[River] Impossible to keep growing:" << R.Size() - nbAssigned << "nodes without rank";
				break;
			}
		}
	}
}

// Same as IsoVectoGenerationV1::PreProcess, plus the reservation of river nodes
void IsoVectoGenerationRiver::PreProcessRiver()
{
	nbAssigned = 0;
	lastChosen = -1;
	nextSeed = 0;
	stats = Stats();

	if (mode == Mode::Reserve)
	{
		for (const Seed& s : seeds)
			R[s.node] = RESERVED_VALUE;
	}

	for (int nodeId = 0; nodeId < R.Size(); ++nodeId)
	{
		// Every border node belongs to the first iso (a river mouth on the coast too)
		if (R.IsBorder(nodeId))
		{
			borders.insert(nodeId);
			R[nodeId] = GetNextHeight();
		}
	}

	if (borders.isEmpty())
		qWarning() << "[River] There is no border in the zone, this is not possible to grow.";
}

void IsoVectoGenerationRiver::ActivateSeed(int node, bool forced)
{
	if (R[node] == INITIAL_VALUE || R[node] == RESERVED_VALUE)
	{
		R[node] = GetNextHeight();
		borders.insert(node);
		if (forced)
			stats.forcedEarly++;
		else
			stats.activatedOnTarget++;
	}
	else
	{
		stats.alreadyAssigned++;
	}
}

void IsoVectoGenerationRiver::ActivateSeedsOnTarget()
{
	while (nextSeed < seeds.size() && seeds[nextSeed].targetRank <= nbAssigned)
	{
		ActivateSeed(seeds[nextSeed].node, false);
		++nextSeed;
	}
}

bool IsoVectoGenerationRiver::ForceNextSeed()
{
	if (nextSeed >= seeds.size())
		return false;

	ActivateSeed(seeds[nextSeed].node, true);
	++nextSeed;
	return true;
}

// Same as IsoVectoGenerationV1::ChooseNextNode, but reports an empty front instead of exiting
bool IsoVectoGenerationRiver::GrowOneNode()
{
	while (true)
	{
		int parent = PickBorderNode();
		if (parent == -1)
			return false;

		// Reserved river nodes are not INITIAL_VALUE, so the growth skips them
		QVector<int> neighs;
		for (int neigh : R.Neighbours(parent))
		{
			if (R[neigh] == INITIAL_VALUE)
				neighs.append(neigh);
		}

		if (!neighs.empty())
		{
			lastChosen = neighs[rNeighbour.Integer(neighs.size())];
			R[lastChosen] = GetNextHeight();
			borders.insert(lastChosen);
			return true;
		}

		borders.remove(parent);
	}
}

// Same as IsoVectoGenerationV1::GetRandomNode: border node chosen with probability P
int IsoVectoGenerationRiver::PickBorderNode()
{
	double cumul = 0;
	for (int ind : borders)
		cumul += P[ind];

	if (cumul == 0)
		return -1;

	double p = rBorder.Uniform(0, cumul);
	for (int ind : borders)
	{
		p -= P[ind];
		if (p <= 0)
			return ind;
	}

	qWarning() << "[River] PickBorderNode: rounding problem";
	return *borders.begin();
}
