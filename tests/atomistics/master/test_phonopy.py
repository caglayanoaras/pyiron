# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import os
import unittest
from pyiron.atomistics.structure.atoms import CrystalStructure
from pyiron_base import Project



class TestPhonopy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_location = os.path.dirname(os.path.abspath(__file__))
        cls.project = Project(os.path.join(cls.file_location, "test_phonopy"))
        cls.project.remove_jobs_silently(recursive=True)

    @classmethod
    def tearDownClass(cls):
        cls.file_location = os.path.dirname(os.path.abspath(__file__))
        cls.project.remove(enable=True, enforce=True)

    def test_run(self):
        job = self.project.create_job(
            'HessianJob', "job_test"
        )
        basis = CrystalStructure(
            element="Fe", bravais_basis="bcc", lattice_constant=2.85
        )
        basis.set_initial_magnetic_moments([2]*len(basis))
        job.set_reference_structure(basis)
        phono = job.create_job("PhonopyJob", "phono")
        structure = phono.list_structures()[0]
        magmoms = structure.get_initial_magnetic_moments()
        self.assertAlmostEqual(sum(magmoms-2), 0)
        rep = phono._phonopy_supercell_matrix().diagonal().astype(int)
        job._reference_structure.set_repeat(rep)
        job.structure.set_repeat(rep)
        job.set_force_constants(1)
        # phono.run() # removed because somehow it's extremely slow


if __name__ == "__main__":
    unittest.main()
