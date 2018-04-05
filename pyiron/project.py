# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from __future__ import print_function
import os
import posixpath
import numpy as np
from string import punctuation
from pyiron_base.project import Project as ProjectCore
try:
    from pyiron_base.core.project.gui import ProjectGUI
except (ImportError, TypeError, AttributeError):
    pass
from pyiron_base.core.settings.generic import Settings
from pyiron_base.objects.generic.hdfio import ProjectHDFio
from pyiron_atomistics.job.jobtype import JobType, JobTypeChoice
from pyiron_atomistics.job.object_type import ObjectType, ObjectTypeChoice
from pyiron_atomistics.structure.periodic_table import PeriodicTable
from pyiron_lammps.potential import LammpsPotentialFile
from pyiron_vasp.potential import VaspPotential
from pyiron_atomistics.structure.atoms import CrystalStructure
import pyiron_atomistics.structure.pyironase as ase
from pyiron_atomistics.structure.atoms import Atoms


__author__ = "Joerg Neugebauer, Jan Janssen"
__copyright__ = "Copyright 2017, Max-Planck-Institut für Eisenforschung GmbH " \
                "- Computational Materials Design (CM) Department"
__version__ = "1.0"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Sep 1, 2017"

assert (isinstance(ase.__file__, str))

s = Settings()


class Project(ProjectCore):
    """
    The project is the central class in pyiron, all other objects can be created from the project object.

    Args:
        path (GenericPath, str): path of the project defined by GenericPath, absolute or relative (with respect to
                                     current working directory) path
        user (str): current pyiron user
        sql_query (str): SQL query to only select a subset of the existing jobs within the current project

    Attributes:

        .. attribute:: root_path

            the pyiron user directory, defined in the .pyiron configuration

        .. attribute:: project_path

            the relative path of the current project / folder starting from the root path
            of the pyiron user directory

        .. attribute:: path

            the absolute path of the current project / folder

        .. attribute:: base_name

            the name of the current project / folder

        .. attribute:: history

            previously opened projects / folders

        .. attribute:: parent_group

            parent project - one level above the current project

        .. attribute:: user

            current unix/linux/windows user who is running pyiron

        .. attribute:: sql_query

            an SQL query to limit the jobs within the project to a subset which matches the SQL query.

        .. attribute:: db

            connection to the SQL database

        .. attribute:: job_type

            Job Type object with all the available job types: ['StructureContainer’, ‘StructurePipeline’, ‘AtomisticExampleJob’,
                                             ‘ExampleJob’, ‘Lammps’, ‘KMC’, ‘Sphinx’, ‘Vasp’, ‘GenericMaster’,
                                             ‘SerialMaster’, ‘AtomisticSerialMaster’, ‘ParallelMaster’, ‘KmcMaster’,
                                             ‘ThermoLambdaMaster’, ‘RandomSeedMaster’, ‘MeamFit’, ‘Murnaghan’,
                                             ‘MinimizeMurnaghan’, ‘ElasticMatrix’, ‘ConvergenceVolume’,
                                             ‘ConvergenceEncutParallel’, ‘ConvergenceKpointParallel’, ’PhonopyMaster’,
                                             ‘DefectFormationEnergy’, ‘LammpsASE’, ‘PipelineMaster’,
                                             ’TransformationPath’, ‘ThermoIntEamQh’, ‘ThermoIntDftEam’, ‘ScriptJob’,
                                             ‘ListMaster']
    """
    def __init__(self, path="", user=None, sql_query=None):
        super(Project, self).__init__(path=path, user=user, sql_query=sql_query)
        self.job_type = JobTypeChoice()
        self.object_type = ObjectTypeChoice()

    def create_job(self, job_type, job_name):
        """
        Create one of the following jobs:
        - 'StructureContainer’:
        - ‘StructurePipeline’:
        - ‘AtomisticExampleJob’: example job just generating random number
        - ‘ExampleJob’: example job just generating random number
        - ‘Lammps’:
        - ‘KMC’:
        - ‘Sphinx’:
        - ‘Vasp’:
        - ‘GenericMaster’:
        - ‘SerialMaster’: series of jobs run in serial
        - ‘AtomisticSerialMaster’:
        - ‘ParallelMaster’: series of jobs run in parallel
        - ‘KmcMaster’:
        - ‘ThermoLambdaMaster’:
        - ‘RandomSeedMaster’:
        - ‘MeamFit’:
        - ‘Murnaghan’:
        - ‘MinimizeMurnaghan’:
        - ‘ElasticMatrix’:
        - ‘ConvergenceVolume’:
        - ‘ConvergenceEncutParallel’:
        - ‘ConvergenceKpointParallel’:
        - ’PhonopyMaster’:
        - ‘DefectFormationEnergy’:
        - ‘LammpsASE’:
        - ‘PipelineMaster’:
        - ’TransformationPath’:
        - ‘ThermoIntEamQh’:
        - ‘ThermoIntDftEam’:
        - ‘ScriptJob’: Python script or jupyter notebook job container
        - ‘ListMaster': list of jobs

        Args:
            job_type (str): job type can be ['StructureContainer’, ‘StructurePipeline’, ‘AtomisticExampleJob’,
                                             ‘ExampleJob’, ‘Lammps’, ‘KMC’, ‘Sphinx’, ‘Vasp’, ‘GenericMaster’,
                                             ‘SerialMaster’, ‘AtomisticSerialMaster’, ‘ParallelMaster’, ‘KmcMaster’,
                                             ‘ThermoLambdaMaster’, ‘RandomSeedMaster’, ‘MeamFit’, ‘Murnaghan’,
                                             ‘MinimizeMurnaghan’, ‘ElasticMatrix’, ‘ConvergenceVolume’,
                                             ‘ConvergenceEncutParallel’, ‘ConvergenceKpointParallel’, ’PhonopyMaster’,
                                             ‘DefectFormationEnergy’, ‘LammpsASE’, ‘PipelineMaster’,
                                             ’TransformationPath’, ‘ThermoIntEamQh’, ‘ThermoIntDftEam’, ‘ScriptJob’,
                                             ‘ListMaster']
            job_name (str): name of the job

        Returns:
            GenericJob: job object depending on the job_type selected
        """
        job = JobType(job_type, project=ProjectHDFio(project=self.copy(), file_name=job_name),
                      job_name=job_name)
        if self.user is not None:
            job.user = self.user
        return job

    @staticmethod
    def create_object(object_type):
        """

        Args:
            object_type:

        Returns:

        """
        obj = ObjectType(object_type, project=None, job_name=None)
        return obj

    def copy(self):
        """
        Copy the project object - copying just the Python object but maintaining the same pyiron path

        Returns:
            Project: copy of the project object
        """
        new = Project(path=self.path, user=self.user, sql_query=self.sql_query)
        new._filter = self._filter
        new._inspect_mode = self._inspect_mode
        return new

    def load_from_jobpath(self, job_id=None, db_entry=None, convert_to_object=True):
        """
        Internal function to load an existing job either based on the job ID or based on the database entry dictionary.

        Args:
            job_id (int): Job ID - optional, but either the job_id or the db_entry is required.
            db_entry (dict): database entry dictionary - optional, but either the job_id or the db_entry is required.
            convert_to_object (bool): convert the object to an pyiron object or only access the HDF5 file - default=True
                                      accessing only the HDF5 file is about an order of magnitude faster, but only
                                      provides limited functionality. Compare the GenericJob object to JobCore object.

        Returns:
            GenericJob, JobCore: Either the full GenericJob object or just a reduced JobCore object
        """
        job = super(Project, self).load_from_jobpath(job_id=job_id, db_entry=db_entry,
                                                     convert_to_object=convert_to_object)
        job.project_hdf5._project = Project(path=job.project_hdf5.file_path)
        return job

    def import_single_calculation(self, project_to_import_from, rel_path=None, job_type="Vasp"):
        """

        Args:
            rel_path:
            project_to_import_from:
            job_type (str): Type of the calculation which is going to be imported
        """
        if job_type not in ['Vasp', 'KMC']:
            raise ValueError('The job_type is not supported.')
        job_name = project_to_import_from.split("/")[-1]
        if job_name[0].isdigit():
            pyiron_job_name = 'job_' + job_name
        else:
            pyiron_job_name = job_name
        for ch in list(punctuation):
            if ch in pyiron_job_name:
                pyiron_job_name = pyiron_job_name.replace(ch, '_')
        print(job_name, pyiron_job_name)
        if rel_path:
            rel_path_lst = [pe for pe in rel_path.split("/")[:-1] if pe != '..']
            pr_import = self.open('/'.join(rel_path_lst))
        else:
            pr_import = self.open('/'.join(project_to_import_from.split("/")[:-1]))
        if self.db.get_items_dict({'job': pyiron_job_name, 'project': pr_import.project_path}):
            print('The job exists already - skipped!')
        else:
            ham = pr_import.create_job(job_type=job_type, job_name=pyiron_job_name)
            ham._job_id = self.db.add_item_dict(ham.db_entry())
            ham.refresh_job_status()
            print('job was stored with the job ID ', str(ham._job_id))
            ham.from_directory(os.path.join(self.path, project_to_import_from).replace('\\', '/'))

    def import_from_path(self, path, recursive=True):
        """

        Args:
            path:
            recursive:

        Returns:

        """
        search_path = posixpath.normpath(posixpath.join(self.path, path))
        if recursive:
            for x in os.walk(search_path):
                self._calculation_validation(x[0], x[2], rel_path=posixpath.relpath(x[0], search_path))
        else:
            abs_path = '/'.join(search_path.split("/")[:-1])
            rel_path = posixpath.relpath(abs_path, self.path)
            self._calculation_validation(search_path, os.listdir(search_path), rel_path=rel_path)

    def _calculation_validation(self, path, files_available, rel_path=None):
        """

        Args:
            path:
            files_available:
            rel_path:

        Returns:

        """
        if "OUTCAR" in files_available or "vasprun.xml" in files_available or "OUTCAR.gz" in files_available or \
                        "vasprun.xml.bz2" in files_available:
            self.import_single_calculation(path, rel_path=rel_path, job_type="Vasp")
        if "incontrol.dat" in files_available and "lattice.out" in files_available and "lattice.inp" in files_available:
            self.import_single_calculation(path, rel_path=rel_path, job_type="KMC")

    @staticmethod
    def create_structure(element, bravais_basis, lattice_constant):
        """
        
        Args:
            element: 
            bravais_basis: 
            lattice_constant: 

        Returns:

        """
        return CrystalStructure(element=element, bravais_basis=bravais_basis, lattice_constants=[lattice_constant])

    @staticmethod
    def create_ase_bulk(name, crystalstructure=None, a=None, c=None, covera=None, u=None,
                        orthorhombic=False, cubic=False):
            """Creating bulk systems using ASE bulk module.

            Crystal structure and lattice constant(s) will be guessed if not
            provided.

            name: str
                Chemical symbol or symbols as in 'MgO' or 'NaCl'.
            crystalstructure: str
                Must be one of sc, fcc, bcc, hcp, diamond, zincblende,
                rocksalt, cesiumchloride, fluorite or wurtzite.
            a: float
                Lattice constant.
            c: float
                Lattice constant.
            c_over_a: float
                c/a ratio used for hcp.  Default is ideal ratio: sqrt(8/3).
            u: float
                Internal coordinate for Wurtzite structure.
            orthorhombic: bool
                Construct orthorhombic unit cell instead of primitive cell
                which is the default.
            cubic: bool
                Construct cubic unit cell if possible.
            """
            from ase.build import bulk
            return bulk(name=name, crystalstructure=crystalstructure, a=a, c=c, covera=covera, u=u,
                        orthorhombic=orthorhombic, cubic=cubic)

    @staticmethod
    def create_atoms(symbols=None, positions=None, numbers=None, tags=None, momenta=None, masses=None,
                 magmoms=None, charges=None, scaled_positions=None, cell=None, pbc=None, celldisp=None, constraint=None,
                 calculator=None, info=None, indices=None, elements=None, dimension=None, species=None,
                 **qwargs):
        """
        Creates a pyiron_atomistics.structure.atoms.Atoms instance.

        """
        return Atoms(symbols=None, positions=None, numbers=None, tags=None, momenta=None, masses=None,
                     magmoms=None, charges=None, scaled_positions=None, cell=None, pbc=None, celldisp=None,
                     constraint=None, calculator=None, info=None, indices=None, elements=None, dimension=None,
                     species=None, **qwargs)

    setattr(create_atoms, '__doc__', create_atoms.__doc__ + Atoms.__doc__)

    @staticmethod
    def create_surface(element, surface_type, size=(1, 1, 1), vacuum=1.0, center=False, **kwargs):
        """
        Generates surfaces instances based on the ase.build.surface module.
        Args:
            element (str): Element name
            surface_type (str): The string specifying the surface type generators available through ase (fcc111,
            hcp0001 etc.)
            size (turple): Size of the surface
            vacuum (float): Length of vacuum layer added to the surface along the z direction
            center (boolean): Tells if the surface layers have to be at the center or at one end along the z-direction
            **kwargs: Additional, arguments you would normally pass to the structure generator like 'a', 'b',
            'orthogonal' etc.

        Returns:
            surface (pyiron_atomistics.structure.atoms.Atoms instance)

        """
        # https://gitlab.com/ase/ase/blob/master/ase/lattice/surface.py
        from ase.build import (add_adsorbate, add_vacuum,
                               bcc100, bcc110, bcc111,
                               diamond100, diamond111,
                               fcc100, fcc110, fcc111, fcc211,
                               hcp0001, hcp10m10, mx2,
                               hcp0001_root, fcc111_root, bcc111_root,
                               root_surface, root_surface_analysis, surface)
        if surface_type in [add_adsorbate.__name__, add_vacuum.__name__,
                            bcc100.__name__, bcc110.__name__, bcc111.__name__,
                            diamond100.__name__, diamond111.__name__,
                            fcc100.__name__, fcc110.__name__, fcc111.__name__, fcc211.__name__,
                            hcp0001.__name__, hcp10m10.__name__, mx2.__name__,
                            hcp0001_root.__name__, fcc111_root.__name__, bcc111_root.__name__,
                            root_surface.__name__, root_surface_analysis.__name__, surface.__name__]:
            surface_type = eval(surface_type)
            if center:
                surface = surface_type(symbol=element, size=size, vacuum=vacuum, **kwargs)
            else:
                surface = surface_type(symbol=element, size=size, **kwargs)
                z_max = np.max(surface.positions[:, 2])
                surface.cell[2, 2] = z_max + vacuum
            return surface
        else:
            return None

    @staticmethod
    def inspect_periodic_table():
        return PeriodicTable()

    @staticmethod
    def inspect_emperical_potentials():
        return LammpsPotentialFile()

    @staticmethod
    def inspect_pseudo_potentials():
        return VaspPotential()

    @staticmethod
    def create_element(parent_element, new_element_name=None, spin=None, potential_file=None):
        """
        
        Args:
            parent_element (str, int): The parent element eq. "N", "O", "Mg" etc.
            new_element_name (str): The name of the new parent element (can be arbitrary)
            spin (float): Value of the magnetic moment (with sign)
            potential_file (str): Location of the new potential file if necessary

        Returns:
            pyiron_atomistics.structure.periodic_table.ChemicalElement instance
        """
        periodic_table = PeriodicTable()
        if new_element_name is None:
            if spin is not None:
                new_element_name = parent_element + '_spin_' + str(spin).replace('.', '_')
            else:
                new_element_name = parent_element + "_1"
        if potential_file is not None:
            if spin is not None:
                periodic_table.add_element(parent_element=parent_element, new_element=new_element_name,
                                                         spin=str(spin), pseudo_potcar_file=potential_file)
            else:
                periodic_table.add_element(parent_element=parent_element, new_element=new_element_name,
                                                         pseudo_potcar_file=potential_file)
        elif spin is not None:
            periodic_table.add_element(parent_element=parent_element, new_element=new_element_name,
                                                     spin=str(spin))
        else:
            periodic_table.add_element(parent_element=parent_element, new_element=new_element_name)
        return periodic_table.element(new_element_name)

    # Graphical user interfaces
    def gui(self):
        """
        
        Returns:

        """
        ProjectGUI(self)