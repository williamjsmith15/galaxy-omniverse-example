import FreeCAD
import Part
import argparse

# Load the STEP file
doc = FreeCAD.newDocument()
Part.insert("file_to_import.step", doc.Name)

# Get the active object (assuming the STEP file has one main object)
obj = doc.ActiveObject

# Calculate the bounding box
bbox = obj.Shape.BoundBox

parser = argparse.ArgumentParser()
parser.add_argument('output_file_path')
args = parser.parse_args()
output_file = args.output_file_path

# Write the bounding box dimensions to a file, rounding to 5 decimal places
with open(output_file, "w") as file:
    file.write("Min/Max,X,Y,Z\n")

    # Write the data with rounding
    file.write(f"Min,{round(bbox.XMin, 5)},{round(bbox.YMin, 5)},{round(bbox.ZMin, 5)}\n")
    file.write(f"Max,{round(bbox.XMax, 5)},{round(bbox.YMax, 5)},{round(bbox.ZMax, 5)}\n")

FreeCAD.closeDocument(doc.Name)
