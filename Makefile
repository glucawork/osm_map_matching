# Directory sorgente
SRC_DIR := .

# Controllo del sistema operativo
HOSTNAME := $(shell hostname)

# Definizione della directory di destinazione in base al sistema operativo
ifeq ($(HOSTNAME), DESKTOP-HFQA6RH) # debian su lenovo
    DEST_DIR := /mnt/c/Users/gianluca/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/osm_map_matching/
else ifeq ($(HOSTNAME), dell16)
    DEST_DIR := /home/gianluca/.local/share/QGIS/QGIS3/profiles/default/python/plugins/osm_map_matching
else ifeq ($(HOSTNAME), DESKTOP-Q39571R)
	DEST_DIR := /mnt/c/Users/gluca/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/osm_map_matching/ 
else
    DEST_DIR := 
endif

# Lista dei file da copiare
FILES := LICENSE README.md __init__.py  i18n/ icon/ icon.png metadata.txt osm_map_matching.py osm_map_matching_algorithm.py osm_map_matching_provider.py output.py pictures/   ta/ test/ 

# Regola predefinita per copiare i file
all: copy_files

# Regola per copiare i file
copy_files:
	cp -r $(addprefix $(SRC_DIR)/, $(FILES)) $(DEST_DIR)


zip:
	mkdir osm_map_matching
	cp -r __init__.py osm_map_matching/.
	cp -r README.md osm_map_matching/.
	cp -r LICENSE osm_map_matching/.
	cp -r metadata.txt osm_map_matching/.
	cp -r icon.png osm_map_matching/.
	cp -r osm_map_matching.py osm_map_matching/.
	cp -r osm_map_matching_algorithm.py osm_map_matching/.
	cp -r osm_map_matching_provider.py osm_map_matching/.
	cp -r output.py osm_map_matching/.
	cp -r ta osm_map_matching/.
	cp -r test osm_map_matching/.
	zip -r osm_map_matching.zip osm_map_matching/
	#rm -rf osm_map_matching/
