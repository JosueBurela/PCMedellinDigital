// ==============================================================================
//  🗺️ GEOMETRÍAS Y POLÍGONOS GEOJSON DE MEDELLÍN DE BRAVO, VERACRUZ
//  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
// ==============================================================================

const MEDELLIN_TERRITORIO_GEOJSON = {
  "type": "FeatureCollection",
  "features": [

    // =========================================================================
    // 1. PERÍMETRO MUNICIPAL DE MEDELLÍN DE BRAVO
    // =========================================================================
    {
      "type": "Feature",
      "properties": {
        "nombre": "Municipio de Medellín de Bravo",
        "tipo": "MUNICIPAL",
        "categoria": "Perímetro Municipal",
        "descripcion": "Límite territorial oficial del Municipio de Medellín de Bravo, Veracruz."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.2200, 19.1100],
          [-96.1600, 19.1200],
          [-96.1200, 19.0900],
          [-96.0800, 19.0600],
          [-96.0900, 18.9800],
          [-96.1400, 18.9600],
          [-96.2000, 18.9900],
          [-96.2300, 19.0500],
          [-96.2200, 19.1100]
        ]]
      }
    },

    // =========================================================================
    // 2. FRACCIONAMIENTOS
    // =========================================================================
    {
      "type": "Feature",
      "properties": {
        "nombre": "Fraccionamiento Puente Moreno",
        "tipo": "FRACCIONAMIENTO",
        "categoria": "Fraccionamiento de Alta Densidad",
        "descripcion": "Zona habitacional urbana principal de Medellín de Bravo."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1550, 19.0920],
          [-96.1420, 19.0920],
          [-96.1400, 19.0800],
          [-96.1520, 19.0780],
          [-96.1560, 19.0860],
          [-96.1550, 19.0920]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Fraccionamiento Arboledas San Ramón",
        "tipo": "FRACCIONAMIENTO",
        "categoria": "Fraccionamiento",
        "descripcion": "Desarrollo habitacional colindante con Puente Moreno y El Tejar."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1580, 19.0880],
          [-96.1500, 19.0880],
          [-96.1490, 19.0790],
          [-96.1570, 19.0790],
          [-96.1580, 19.0880]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Fraccionamiento Lagos de Puente Moreno",
        "tipo": "FRACCIONAMIENTO",
        "categoria": "Fraccionamiento",
        "descripcion": "Etapa de desarrollo habitacional con áreas lacustres y parque recreativo."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1480, 19.0960],
          [-96.1380, 19.0950],
          [-96.1370, 19.0860],
          [-96.1460, 19.0870],
          [-96.1480, 19.0960]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Fraccionamiento Arboledas de San Miguel",
        "tipo": "FRACCIONAMIENTO",
        "categoria": "Fraccionamiento",
        "descripcion": "Zona residencial de crecimiento en la zona norte de Medellín."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1620, 19.0980],
          [-96.1540, 19.0980],
          [-96.1530, 19.0900],
          [-96.1610, 19.0900],
          [-96.1620, 19.0980]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Fraccionamiento Paseo Campestre",
        "tipo": "FRACCIONAMIENTO",
        "categoria": "Fraccionamiento / Campestre",
        "descripcion": "Zona habitacional campestre sobre corredor carretero."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1450, 19.0740],
          [-96.1350, 19.0740],
          [-96.1340, 19.0660],
          [-96.1440, 19.0660],
          [-96.1450, 19.0740]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Fraccionamiento La Joya",
        "tipo": "FRACCIONAMIENTO",
        "categoria": "Fraccionamiento Residencial",
        "descripcion": "Zona residencial cercana al río Jamapa."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1650, 19.0720],
          [-96.1560, 19.0720],
          [-96.1550, 19.0640],
          [-96.1640, 19.0640],
          [-96.1650, 19.0720]
        ]]
      }
    },

    // =========================================================================
    // 3. LOCALIDADES Y EJIDOS PRINCIPALES
    // =========================================================================
    {
      "type": "Feature",
      "properties": {
        "nombre": "El Tejar",
        "tipo": "LOCALIDAD",
        "categoria": "Localidad Conurbada Principal",
        "descripcion": "Centro de comercio y alta densidad de población conurbada."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1660, 19.0850],
          [-96.1550, 19.0850],
          [-96.1540, 19.0710],
          [-96.1650, 19.0710],
          [-96.1660, 19.0850]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Medellín (Cabecera Municipal)",
        "tipo": "LOCALIDAD",
        "categoria": "Cabecera Municipal",
        "descripcion": "Sede histórica del Palacio Municipal de Medellín de Bravo."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1620, 19.0600],
          [-96.1480, 19.0600],
          [-96.1470, 19.0480],
          [-96.1610, 19.0480],
          [-96.1620, 19.0600]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Playa de Vacas",
        "tipo": "LOCALIDAD",
        "categoria": "Localidad / Ribera del Río",
        "descripcion": "Zona residencial y agrícola a orillas del río Jamapa."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1420, 19.1080],
          [-96.1280, 19.1080],
          [-96.1270, 19.0960],
          [-96.1410, 19.0960],
          [-96.1420, 19.1080]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Paso del Toro",
        "tipo": "LOCALIDAD",
        "categoria": "Nodo Carretero y Comercial",
        "descripcion": "Cruce estratégico de la Federal 180 y carretera a Alvarado/Cordoba."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1480, 19.0420],
          [-96.1280, 19.0420],
          [-96.1270, 19.0250],
          [-96.1470, 19.0250],
          [-96.1480, 19.0420]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Los Robles",
        "tipo": "LOCALIDAD",
        "categoria": "Localidad Agrícola",
        "descripcion": "Comunidad al sur del municipio de Medellín."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1750, 19.0200],
          [-96.1550, 19.0200],
          [-96.1540, 19.0020],
          [-96.1740, 19.0020],
          [-96.1750, 19.0200]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Dos Bocas",
        "tipo": "LOCALIDAD",
        "categoria": "Localidad / Termoeléctrica",
        "descripcion": "Comunidad ribereña e industrial del municipio."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1350, 19.0620],
          [-96.1150, 19.0620],
          [-96.1140, 19.0450],
          [-96.1340, 19.0450],
          [-96.1350, 19.0620]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Rancho del Padre",
        "tipo": "LOCALIDAD",
        "categoria": "Localidad Ejidal",
        "descripcion": "Zona agrícola y ganadera al poniente del municipio."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.2050, 19.0650],
          [-96.1850, 19.0650],
          [-96.1840, 19.0480],
          [-96.2040, 19.0480],
          [-96.2050, 19.0650]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "nombre": "Paso Colorado",
        "tipo": "LOCALIDAD",
        "categoria": "Localidad Ejidal",
        "descripcion": "Comunidad agrícola cercana a la carretera a Paso del Toro."
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-96.1850, 19.0420],
          [-96.1680, 19.0420],
          [-96.1670, 19.0280],
          [-96.1840, 19.0280],
          [-96.1850, 19.0420]
        ]]
      }
    }
  ]
};
