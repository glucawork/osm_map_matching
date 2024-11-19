# Directory sorgente
SRC_DIR := .

# Controllo del sistema operativo
HOSTNAME := $(shell hostname)

# Definizione della directory di destinazione in base al sistema operativo
ifeq ($(HOSTNAME), DESKTOP-HFQA6RH) # debian su lenovo
    DEST_DIR := /mnt/c/Users/gianluca/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/osm_map_matching/
else ifeq ($(HOSTNAME), dell16)
    DEST_DIR := /home/gianluca/.local/share/QGIS/QGIS3/profiles/default/python/plugins/osm_map_matching  
else
    DEST_DIR := 
endif

# Lista dei file da copiare
FILES := LICENSE README.md __init__.py  i18n/ icon/ icon.png metadata.txt osm_map_matching.py osm_map_matching_algorithm.py osm_map_matching_provider.py output.py pb_tool.cfg pictures/  pylintrc  ta/ test/ 

# Regola predefinita per copiare i file
all: copy_files

# Regola per copiare i file
copy_files:
	cp -r $(addprefix $(SRC_DIR)/, $(FILES)) $(DEST_DIR)


#zip:
#	mkdir fitloader
#	cp -r __init__.py fitloader/.
#	cp -r main.py fitloader/.
#	cp -r attribute_table.jpg fitloader/.
#	cp -r icons/ fitloader/.
#	cp -r fit_files/ fitloader/.
#	cp -r README.md fitloader/.
#	cp -r LICENSE fitloader/.
#	cp -r metadata.txt fitloader/.
#	zip -r fitloader.zip fitloader/
#	rm -r fitloader
