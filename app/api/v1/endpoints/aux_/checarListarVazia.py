from app.domain.models import indicador
from app.domain.models.anexo import Anexo
from app.domain.models.posicao import Posicao
def checarListaVazia(lista_all:list, lista_json:list, inserirPosicao:bool, session):
    if len(lista_all) == 0:
        pass
    else:
        for element in lista_all:
            json_element:dict = {}
            json_element["nome"] = element.nome
            if(inserirPosicao):
                if isinstance(element, indicador.Indicador):
                    posicao = session.query(Posicao).filter(Posicao.fkIndicador_id == element.id).first()
                    if posicao is not None:
                        json_element["posicao"] = posicao.posicao
                elif isinstance(element, Anexo):
                    posicao = session.query(Posicao).filter(Posicao.fkAnexo_id == element.id).first()
                    if posicao is not None:
                        json_element["posicao"] = posicao.posicao
            else:
                json_element["posicao"] = None
            lista_json.append(json_element)