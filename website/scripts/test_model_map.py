#!/usr/bin/env python3
"""Numerical regression tests; no model calls and no expensive projection refit."""
import hashlib
import json
from pathlib import Path
import unittest

import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

import generate_map as gm


class GeometryTests(unittest.TestCase):
    def test_one_scale_preserves_relative_distances(self):
        x = np.array([[0., 0., 0.], [1., 3., 0.], [2., 0., 7.]])
        y = gm.normalise_projection(x)
        a, b = euclidean_distances(x), euclidean_distances(y)
        ratios = b[a > 0] / a[a > 0]
        self.assertLess(float(np.ptp(ratios)), 1e-6)
        self.assertEqual(y.dtype, np.float64)

    def test_duplicates_exclude_self_with_stable_ties(self):
        d = np.zeros((5, 5))
        nn = gm.nearest_indices(d, 3)
        for i, row in enumerate(nn):
            self.assertNotIn(i, row)
            self.assertEqual(list(row), [j for j in range(5) if j != i][:3])

    def test_exact_projection_and_scale_have_zero_error(self):
        x = np.array([[0., 0.], [1., 0.], [1., 3.], [5., 2.], [-3., 4.]])
        q = gm.projection_quality(euclidean_distances(x), x * 12)
        self.assertEqual(q['retained'], [3] * 5)
        self.assertEqual(q['knn3'], 1)
        self.assertLess(q['distance_error'], 1e-12)

    def test_provenance_does_not_invent_capture_dates(self):
        rows = [{'source': 'v2', 'cell': 'a', 'condition': 'SHORT', 'release_date': '2020-01-01'},
                {'source': 'v2', 'cell': 'b', 'condition': 'LONG'}]
        p = gm.sample_provenance(rows)
        self.assertEqual((p['samples'], p['cell_count']), (2, 2))
        self.assertIsNone(p['capture_dates'])
        self.assertEqual(p['conditions'], {'LONG': 1, 'SHORT': 1})


class ShippedMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(gm.OUT.read_text())
        cls.models = cls.data['models']
        cls.sim = np.array(cls.data['sim'])
        cls.dist = 1 - cls.sim

    def test_payload_shape_and_provenance(self):
        d = self.data
        self.assertEqual(d['schema_version'], 2)
        self.assertEqual(d['order'], [m['model'] for m in self.models])
        self.assertEqual(len(set(d['order'])), len(self.models))
        self.assertEqual(self.sim.shape, (len(self.models), len(self.models)))
        np.testing.assert_allclose(self.sim, self.sim.T, atol=1e-12)
        np.testing.assert_allclose(self.sim.diagonal(), 1)
        self.assertTrue(np.isfinite(self.sim).all())
        self.assertEqual(set(d['projections']), {'pca2', 'pca3', 'mds2', 'mds3', 'umap2', 'umap3'})
        self.assertEqual(sum(m['provenance']['samples'] for m in self.models), d['generated_from']['freeflow_docs'])
        self.assertEqual(d['generated_from']['generator_sha256'], hashlib.sha256(Path(gm.__file__).read_bytes()).hexdigest())

    def test_published_scores_recompute_from_published_data(self):
        for key, expected in self.data['projections'].items():
            with self.subTest(key=key):
                x = np.array([m['coords'][key] for m in self.models])
                self.assertEqual(x.shape[1], int(key[-1]))
                self.assertTrue(np.isfinite(x).all())
                q = gm.projection_quality(self.dist, x)
                self.assertAlmostEqual(expected['knn3'], q['knn3'], places=10)
                self.assertAlmostEqual(expected['distance_error'], q['distance_error'], places=9)
                for i, m in enumerate(self.models):
                    self.assertEqual(m['fidelity'][key]['retained'], q['retained'][i])
                    self.assertEqual(m['fidelity'][key]['projected_nn'], [self.data['order'][j] for j in q['projected_nn'][i]])

    def test_neighbours_and_actual_samples(self):
        nn = gm.nearest_indices(self.dist, 6)
        for i, m in enumerate(self.models):
            with self.subTest(model=m['model']):
                self.assertEqual([v[0] for v in m['nn']], [self.data['order'][j] for j in nn[i]])
                samples = json.loads((gm.SAMPLES / f'{m["model"]}.json').read_text())['samples']
                samples = [s for s in samples if s['type'] == 'freeflow' and s.get('result')]
                self.assertEqual(m['provenance'], gm.sample_provenance(samples))

    def test_tree_has_each_model_once_and_monotone_heights(self):
        def leaves(node, parent=float('inf')):
            if 'm' in node:
                return [node['m']]
            self.assertLessEqual(node['h'], parent + 1e-6)
            self.assertEqual(len(node['c']), 2)
            return [m for c in node['c'] for m in leaves(c, node['h'])]
        self.assertEqual(sorted(leaves(self.data['tree'])), sorted(self.data['order']))


if __name__ == '__main__':
    unittest.main()
