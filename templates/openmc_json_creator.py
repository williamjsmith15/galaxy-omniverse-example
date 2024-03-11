import json

'''
Creates json files for use in the OpenMC workflow tools
'''

minor_radius = 200
major_radius = 620
outer_sphere = major_radius + minor_radius * 2

batches = 5
particles = 1000

openMC_settings = {
	"geometry"  : {
		"minor_radius"	: minor_radius,
		"major_radius"	: major_radius,
		"triangularity" : 0.55,
		"elongation"	: 1,
		"outer_sphere" 	: outer_sphere,
		"first_wall_thickness" : 3,
		"plasma_offset"	: 40,
		"blanket_thickness" : 90,
	},
	"settings"	: {
		"temperature" : 600, 
		"run_mode" : "fixed source",
		"batches"  : batches,
		"particles": particles,
	},
    "plasma_params" : {
	    "plasma_mode"                   : 'H',
	    "ion_density_centre"            : 1.09e20,
        "ion_density_peaking_factor"    : 1,
        "ion_density_pedestal"          : 1.09e20,
        "ion_density_separatrix"        : 3e19,
        "ion_temperature_centre"        : 45.9,
        "ion_temperature_peaking_factor": 8.06,
        "ion_temperature_pedestal"      : 6.09,
        "ion_temperature_separatrix"    : 0.1,
        "shafranov_factor"              : 0.44789,
        "ion_temperature_beta"          : 6,
    },
}

with open('openmc_config.json', 'w') as write_f:
	json.dump(openMC_settings, write_f)