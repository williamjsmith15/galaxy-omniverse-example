from process.io.mfile import MFile

out_dat = MFile(filename='RUN_MFILE.DAT')

te = out_dat.data["te"].get_scans()
print(te[0])
