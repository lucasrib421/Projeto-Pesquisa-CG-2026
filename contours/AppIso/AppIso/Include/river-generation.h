#pragma once

#include "iso-vecto-generation-v1.h"

/*
 * Single-region Open Eden Growth (IsoVectoGenerationV1) extended with
 * user-drawn rivers whose riverbed elevation is prescribed.
 *
 * Each river node has a target rank (the rank whose height, after the
 * histogram mapping, is the requested elevation). The node becomes an extra
 * growth seed when the rank counter reaches its target:
 *   - Mode::Reserve: river nodes are blocked for the natural growth until
 *     their target, so they get exactly the requested rank;
 *   - Mode::Passive: river nodes are not blocked; they get the rank of
 *     whichever comes first, the natural growth or their target;
 *   - Mode::None: no seeds; same algorithm as IsoVectoGenerationV1.
 *
 * The original IsoVectoGenerationV1 is left untouched: the growth loop is
 * reimplemented here so that seeds can be activated between steps.
 */
class IsoVectoGenerationRiver : public IsoVectoGenerationV1
{
public:
	enum class Mode { None, Reserve, Passive };

	struct Seed
	{
		int node;
		int targetRank;
	};

	struct Stats
	{
		int activatedOnTarget = 0;   // seed got its rank when the counter reached the target
		int alreadyAssigned = 0;     // node already had a rank (coast node, or reached by growth in passive mode)
		int forcedEarly = 0;         // reserve mode: front was empty, seed activated before its target
	};

	IsoVectoGenerationRiver(const GraphPoisson&, const ScalarField2&, Mode, const QVector<Seed>&, int seed);

	void Generate();
	Stats GetStats() const;

protected:
	void PreProcessRiver();
	void ActivateSeed(int node, bool forced);
	void ActivateSeedsOnTarget();
	bool ForceNextSeed();
	bool GrowOneNode();
	int PickBorderNode();

	Mode mode;
	QVector<Seed> seeds;   // sorted by target rank
	int nextSeed = 0;
	Random rNeighbour;     // same role as the static generator of IsoVectoGenerationV1::ChooseNextNode
	Random rBorder;        // same role as the static generator of IsoVectoGenerationV1::GetRandomNode
	Stats stats;
};

inline IsoVectoGenerationRiver::Stats IsoVectoGenerationRiver::GetStats() const
{
	return stats;
}
