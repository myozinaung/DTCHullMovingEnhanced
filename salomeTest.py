print("Hello World")

import salomeTest2
salomeTest2.salome_init_without_session()
import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()
 
import tempfile, os

# import IGES file
sphere_iges = geompy.ImportIGES("kcs.igs")
 
# create a sphere
sphere = geompy.MakeSphereR(100)
 
# tmpdir = tempfile.mkdtemp()

# export sphere to the ASCII STL file, with custom deflection coefficient
# f_stl2 = os.path.join(tmpdir, "sphere2.stl")
geompy.ExportSTL(sphere, "sphere2.stl", True, 0.1)