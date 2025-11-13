import osmnx as ox
import geopandas as gpd
import pandas as pd
import logging
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString
from requests.exceptions import ConnectionError
from urllib.error import URLError


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


LISTA_BAIRROS_OFICIAIS = [
    # RPA 1 (Centro)
    "Bairro do Recife", "Boa Vista", "Cabanga", "Coelhos", "Ilha do Leite",
    "Ilha Joana Bezerra", "Paissandu", "Santo Amaro", "Santo Antônio", "São José", "Soledade",
    # RPA 2 (Norte)
    "Água Fria", "Alto Santa Terezinha", "Arruda", "Beberibe", "Bomba do Hemetério",
    "Cajueiro", "Campina do Barreto", "Campo Grande", "Dois Unidos", "Encruzilhada",
    "Fundão", "Hipódromo", "Linha do Tiro", "Peixinhos", "Ponto de Parada",
    "Porto da Madeira", "Rosarinho", "Torreão",
    # RPA 3 (Noroeste)
    "Aflitos", "Alto do Mandu", "Alto José Bonifácio", "Alto José do Pinho", "Apipucos",
    "Brejo da Guabiraba", "Brejo de Beberibe", "Casa Amarela", "Casa Forte",
    "Córrego do Jenipapo", "Derby", "Dois Irmãos", "Espinheiro", "Graças",
    "Guabiraba", "Jaqueira", "Macaxeira", "Mangabeira", "Monteiro",
    "Morro da Conceição", "Nova Descoberta", "Parnamirim", "Passarinho",
    "Pau-Ferro", "Poço da Panela", "Santana", "Sítio dos Pintos", "Tamarineira",
    "Vasco da Gama",
    # RPA 4 (Oeste)
    "Caxangá", "Cidade Universitária", "Cordeiro", "Engenho do Meio", "Ilha do Retiro",
    "Iputinga", "Madalena", "Prado", "Torre", "Torrões", "Várzea", "Zumbi",
    # RPA 5 (Sudoeste)
    "Afogados", "Areias", "Barro", "Bongi", "Caçote", "Coqueiral", "Curado",
    "Estância", "Jardim São Paulo", "Jiquiá", "Mangueira", "Mustardinha",
    "San Martin", "Sancho", "Tejipió", "Totó",
    # RPA 6 (Sul)
    "Boa Viagem", "Brasília Teimosa", "Cohab", "Ibura", "Imbiribeira", "Ipsep",
    "Jordão", "Pina"
]


# Referência pro OSMnx
LUGAR_QUERY = "Recife, Pernambuco, Brasil"

# Sistema de Referência de Coordenadas (CRS), em metros
PROJ_CRS = "EPSG:32725"

GEOJSON_SAIDA = "src/utils/geojson_data/bair_recife.geojson"
CSV_SAIDA = "data/adjacencias_recife.csv"


def fetch_bairro_geometry(bairro_nome: str, lugar_query: str, ) -> gpd.GeoDataFrame | None:
    query = f"{bairro_nome}, {lugar_query}"

    try:
        logging.info(f"Buscando geometria para: {bairro_nome}")
        gdf = ox.geocode_to_gdf(query)

        gdf['bairro_nome'] = bairro_nome
        return gdf
    
    except (ConnectionError, URLError) as e:
        logging.critical(f"Erro de conexão ao buscar '{bairro_nome}'. Erro: {e}")
        raise
    except Exception as e:
        logging.warning(f"Não foi possível encontrar a geometria para: {bairro_nome}. Erro: {e}")


def processar_geometrias(gdfs_list: list) -> gpd.GeoDataFrame:
    logging.info("Combinando geometrias dos bairros...")
    # Concatena todos os GPDs individuais em um único GeoDataFrame
    bairros_gdf = gpd.GeoDataFrame(pd.concat(gdfs_list, ignore_index=True), crs=gdfs_list[0].crs)

    logging.info("Validando e limpando geometrias...")
    bairros_gdf['geometry'] = bairros_gdf.geometry.make_valid()

    logging.info("Dissolvendo geometrias por nome de bairro...")
    bairros_gdf = bairros_gdf.dissolve(by='bairro_nome', as_index=False)

    bairros_gdf = bairros_gdf[['bairro_nome', 'geometry']]

    logging.info(f"Geometrias processadas e validadas para {len(bairros_gdf)} bairros.")
    return bairros_gdf


def calcular_adjacencias(bairros_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    logging.info("Iniciando cálculo de adjacências (divisas diretas)...")
    
    logging.info(f"Reprojetando para {PROJ_CRS} para cálculo de interseção...")
    bairros_gdf_proj = bairros_gdf.to_crs(PROJ_CRS)

    adjacencias = []

    nomes = bairros_gdf_proj['bairro_nome'].to_list()
    geoms = bairros_gdf_proj['geometry'].to_list()

    for i in range(len(nomes)):
        for j in range (i + 1, len(nomes)):
            bairro_A_nome = nomes[i]
            bairro_A_geom = geoms[i]
            bairro_B_nome = nomes[j]
            bairro_B_geom = geoms[j]

            if not bairro_A_geom.intersects(bairro_B_geom):
                continue

            try:
                intersection = bairro_A_geom.intersection(bairro_B_geom)
            
            except Exception as e:
                logging.warning(f"Erro ao calcular interseção entre {bairro_A_nome} e {bairro_B_nome}: {e}")
                continue

            if intersection.is_empty:
                continue

            if isinstance(intersection, (LineString, MultiLineString)):
                adjacencias.append({
                    "bairro_origem": bairro_A_nome,
                    "bairro_destino": bairro_B_nome
                })
                logging.debug(f"Adjacência válida (Linha) encontrada: {bairro_A_nome} <-> {bairro_B_nome}")
            
            elif isinstance(intersection, (Point, MultiPoint)):
                logging.debug(f"Adjacência ignorada (Ponto) entre: {bairro_A_nome} e {bairro_B_nome}")

    logging.info(f"Cálculo concluído. Total de {len(adjacencias)} relações de adjacência encontradas.")

    if not adjacencias:
        return pd.DataFrame(columns=["bairro_origem", "bairro_destino"])
    
    return pd.DataFrame(adjacencias)


def main():
    logging.info(f"--- Iniciando Pipeline de Adjacências de Bairros de Recife ---")
    logging.info(f"Total de bairros a serem processados: {len(LISTA_BAIRROS_OFICIAIS)}")

    gdfs_list = []
    bairros_nao_encontrados = []

    for bairro in LISTA_BAIRROS_OFICIAIS:
        gdf_bairro = fetch_bairro_geometry(bairro, LUGAR_QUERY)
        
        if gdf_bairro is not None and not gdf_bairro.empty:
            gdfs_list.append(gdf_bairro)
        else:
            bairros_nao_encontrados.append(bairro)

    if not gdfs_list:
        logging.error("Nenhuma geometria de bairro foi encontrada. Encerrando o script.")
        return
    
    logging.info(f"Busca concluída. {len(gdfs_list)} bairros encontrados.")

    if bairros_nao_encontrados:
        logging.warning(f"Bairros não encontrados no OSM: {', '.join(bairros_nao_encontrados)}")

    bairros_gdf = processar_geometrias(gdfs_list)

    try: 
        bairros_gdf.to_file(GEOJSON_SAIDA, driver="GeoJSON")
        logging.info(f"Arquivo GeoJSON salvo com sucesso em: {GEOJSON_SAIDA}")

    except Exception as e:
        logging.error(f"Não foi possível salvar o arquivo GeoJSON. Erro: {e}")
        return
    
    adj_df = calcular_adjacencias(bairros_gdf)

    if adj_df.empty:
        logging.warning("Nenhuma adjacência foi encontrada para salvar no CSV.")
    else:
        try:
            adj_df.to_csv(CSV_SAIDA, index=False, encoding='utf-8-sig')
            logging.info(f"Arquivo CSV de adjacências salvo com sucesso em: {CSV_SAIDA}")

        except Exception as e:
            logging.error(f"Não foi possível salvar o arquivo CSV. Erro: {e}")
    
    logging.info(f"--- Pipeline Conclúido ---")

if __name__== "__main__":
    ox.settings.use_cache = True
    ox.settings.log_console = False

    main()