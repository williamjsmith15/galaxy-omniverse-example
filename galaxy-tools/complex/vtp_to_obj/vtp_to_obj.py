import vtk as vtk
import argparse

parser = argparse.ArgumentParser(
    prog='vtp_to_obj.py',
    description = 'Converter to go from vtp to obj file format. Usage: vtp_to_obj.py <input.vtp> <output.obj>'
)

parser.add_argument('in_file', help='.vtp input file')
parser.add_argument('out_file', help='.obj output file')

args = parser.parse_args()

in_file = args.in_file
out_file = args.out_file

reader = vtk.vtkXMLPolyDataReader();
reader.SetFileName(in_file)

tubes = vtk.vtkTubeFilter();
tubes.SetInputConnection(reader.GetOutputPort());

ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

profileMapper = vtk.vtkPolyDataMapper()
profileMapper.SetInputConnection(tubes.GetOutputPort())

profile = vtk.vtkActor() 
profile.SetMapper(profileMapper) 
profile.GetProperty().SetSpecular(.3) 
profile.GetProperty().SetSpecularPower(30) 

ren.AddActor(profile)

writer = vtk.vtkOBJExporter()
writer.SetFilePrefix(out_file.replace('.obj', ''))
writer.SetInput(renWin)
writer.Write()