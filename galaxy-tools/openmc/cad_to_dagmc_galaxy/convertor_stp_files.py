from cad_to_dagmc import CadToDagmc

my_model = CadToDagmc()
my_model.add_stp_file("Vacuum.step", material_tags=["vac"])
my_model.add_stp_file("First_Wall.step", material_tags=["fw"])
my_model.add_stp_file("Plasma.step", material_tags=["plas"])
my_model.add_stp_file("Blanket_I.step", material_tags=["blanket"])

my_model.export_dagmc_h5m_file(max_mesh_size=30, min_mesh_size=20)

