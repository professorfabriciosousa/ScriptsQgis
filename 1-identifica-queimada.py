"""
Model exported as python.
Name : 1-IdentificaQueimadas_22072021
Group : Fire-Mirador-2021
With QGIS : 32205
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterDateTime
from qgis.core import QgsProcessingParameterVectorDestination
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsExpression
import processing


class Identificaqueimadas_22072021(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterString('Gridex22066', 'Grid ex: 220/66', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterRasterLayer('mir', 'NIR1', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('nir', 'MIR1', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('BQA1', 'BQA_1', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('mir (2)', 'NIR2', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('nir (2)', 'MIR2', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('BQA1 (2)', 'BQA_2', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('focos', 'focos-queimada', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterDateTime('inicio', 'data-inicio', type=QgsProcessingParameterDateTime.Date, defaultValue=None))
        self.addParameter(QgsProcessingParameterDateTime('fim', 'data-fim', type=QgsProcessingParameterDateTime.Date, defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorDestination('Cicatrizes', 'cicatrizes', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(30, model_feedback)
        results = {}
        outputs = {}

        # Extrair por atributo
        alg_params = {
            'FIELD': 'ID',
            'INPUT': 'C:/PluginQueimada3x/Grid/grid_L8_Ma_PEZA.shp',
            'OPERATOR': 0,  # =
            'VALUE': parameters['Gridex22066'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairPorAtributo'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # RECORTA-BQA1
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,  # Use Camada de entrada Tipo Dado
            'EXTRA': '',
            'INPUT': parameters['BQA1'],
            'KEEP_RESOLUTION': False,
            'MASK': 'C:/PluginQueimada3x/limites/PE_Mirador_com_ZA.shp',
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Recortabqa1'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # GERA_NBR1
        alg_params = {
            'FNAME': False,
            'FORMULA': '(((a-b)/(a+b)))*(-1)',
            'GRIDS': parameters['mir'],
            'NAME': 'Calculation',
            'RESAMPLING': 3,  # [3] B-Spline Interpolation
            'TYPE': 8,  # [8] 8 byte floating point number
            'USE_NODATA': False,
            'XGRIDS': parameters['nir'],
            'RESULT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Gera_nbr1'] = processing.run('saga:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # GERA_NBR2
        alg_params = {
            'FNAME': False,
            'FORMULA': '(((a-b)/(a+b)))*(-1)',
            'GRIDS': parameters['mir (2)'],
            'NAME': 'Calculation',
            'RESAMPLING': 3,  # [3] B-Spline Interpolation
            'TYPE': 8,  # [8] 8 byte floating point number
            'USE_NODATA': False,
            'XGRIDS': parameters['nir (2)'],
            'RESULT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Gera_nbr2'] = processing.run('saga:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # DNBR12
        alg_params = {
            'FORMULA': '(a-b)*(-1)',
            'GRIDS': outputs['Gera_nbr1']['RESULT'],
            'RESAMPLING': 3,  # [3] B-Spline Interpolation
            'TYPE': 8,  # [8] 8 byte floating point number
            'USE_NODATA': False,
            'XGRIDS': outputs['Gera_nbr2']['RESULT'],
            'RESULT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Dnbr12'] = processing.run('saga:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # RECORTA-BQA2
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,  # Use Camada de entrada Tipo Dado
            'EXTRA': '',
            'INPUT': parameters['BQA1 (2)'],
            'KEEP_RESOLUTION': False,
            'MASK': 'C:/PluginQueimada3x/limites/PE_Mirador_com_ZA.shp',
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Recortabqa2'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # identifica_nuvem_1
        alg_params = {
            'FNAME': False,
            'FORMULA': 'ifelse(a>22000, 1, 0)',
            'GRIDS': outputs['Recortabqa1']['OUTPUT'],
            'NAME': 'Calculation',
            'RESAMPLING': 3,  # [3] B-Spline Interpolation
            'TYPE': 1,  # [1] unsigned 1 byte integer
            'USE_NODATA': False,
            'XGRIDS': None,
            'RESULT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Identifica_nuvem_1'] = processing.run('saga:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # RepFocos
        alg_params = {
            'INPUT': parameters['focos'],
            'OPERATION': '',
            'TARGET_CRS': parameters['mir'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Repfocos'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # identifica_nuvem_2
        alg_params = {
            'FORMULA': 'ifelse(a>22000, 1, 0)',
            'GRIDS': outputs['Recortabqa2']['OUTPUT'],
            'RESAMPLING': 3,  # [3] B-Spline Interpolation
            'TYPE': 1,  # [1] unsigned 1 byte integer
            'USE_NODATA': False,
            'XGRIDS': None,
            'RESULT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Identifica_nuvem_2'] = processing.run('saga:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # nuvem_vetor_2
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['Identifica_nuvem_2']['RESULT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Nuvem_vetor_2'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # fixanuvens2
        alg_params = {
            'INPUT': outputs['Nuvem_vetor_2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Fixanuvens2'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # RECDNBR 12
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,  # Use Camada de entrada Tipo Dado
            'EXTRA': '',
            'INPUT': outputs['Dnbr12']['RESULT'],
            'KEEP_RESOLUTION': False,
            'MASK': 'C:/PluginQueimada3x/limites/PE_Mirador_com_ZA.shp',
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Recdnbr12'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # nuvem_vetor_1
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['Identifica_nuvem_1']['RESULT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Nuvem_vetor_1'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Filtro Simples
        alg_params = {
            'INPUT': outputs['Recdnbr12']['OUTPUT'],
            'KERNEL_RADIUS': 2,
            'KERNEL_TYPE': 1,  # [1] Circle
            'METHOD': 0,  # [0] Smooth
            'RESULT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FiltroSimples'] = processing.run('saga:simplefilter', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # fixanuvens1
        alg_params = {
            'INPUT': outputs['Nuvem_vetor_1']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Fixanuvens1'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # ajustacampodata
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'novadata',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 3,  # Data
            'FORMULA': 'to_date("datahora")',
            'INPUT': outputs['Repfocos']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Ajustacampodata'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Queima_NQueima 12
        alg_params = {
            'FORMULA': 'ifelse(a>0.030, 1, 0)',
            'GRIDS': outputs['FiltroSimples']['RESULT'],
            'RESAMPLING': 3,  # [3] B-Spline Interpolation
            'TYPE': 1,  # [1] unsigned 1 byte integer
            'USE_NODATA': True,
            'XGRIDS': None,
            'RESULT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Queima_nqueima12'] = processing.run('saga:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Extrai-inicio
        alg_params = {
            'FIELD': 'novadata',
            'INPUT': outputs['Ajustacampodata']['OUTPUT'],
            'OPERATOR': 3,  # ≥
            'VALUE': QgsExpression(' @inicio ').evaluate(),
            'FAIL_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Extraiinicio'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # juntanuvens
        alg_params = {
            'CRS': None,
            'LAYERS': [outputs['Fixanuvens1']['OUTPUT'],outputs['Fixanuvens2']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Juntanuvens'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # FocosFaixaData
        alg_params = {
            'FIELD': 'novadata',
            'INPUT': outputs['Extraiinicio']['FAIL_OUTPUT'],
            'OPERATOR': 5,  # ≤
            'VALUE': QgsExpression('@fim').evaluate(),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Focosfaixadata'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # RecortarQNQ
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,  # Use Camada de entrada Tipo Dado
            'EXTRA': '',
            'INPUT': outputs['Queima_nqueima12']['RESULT'],
            'KEEP_RESOLUTION': False,
            'MASK': outputs['ExtrairPorAtributo']['OUTPUT'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Recortarqnq'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # FIXARJUNTANUVENS
        alg_params = {
            'INPUT': outputs['Juntanuvens']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Fixarjuntanuvens'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # DissolverNUVENS
        alg_params = {
            'FIELD': [''],
            'INPUT': outputs['Fixarjuntanuvens']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Dissolvernuvens'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Reprojetar camada
        alg_params = {
            'INPUT': outputs['Focosfaixadata']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:32623'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojetarCamada'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Matriz_Vetor
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['Recortarqnq']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Matriz_vetor'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # FixNvDissol
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 10,
            'END_CAP_STYLE': 0,  # Arredondado
            'INPUT': outputs['Dissolvernuvens']['OUTPUT'],
            'JOIN_STYLE': 0,  # Arredondado
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Fixnvdissol'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Amortecedor
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': 500,
            'END_CAP_STYLE': 0,  # Arredondado
            'INPUT': outputs['ReprojetarCamada']['OUTPUT'],
            'JOIN_STYLE': 0,  # Arredondado
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Amortecedor'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # fixVetorQNQ
        alg_params = {
            'INPUT': outputs['Matriz_vetor']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Fixvetorqnq'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Seleciona-cicatrizes-foco
        alg_params = {
            'INPUT': outputs['Fixvetorqnq']['OUTPUT'],
            'INTERSECT': outputs['Amortecedor']['OUTPUT'],
            'PREDICATE': [0,1,3,4,5,6,7],  # interseccionam,contêm,igual,tocam,Sobrepõem,estão dentro de,cruzam
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Selecionacicatrizesfoco'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Diferença
        alg_params = {
            'A': outputs['Selecionacicatrizesfoco']['OUTPUT'],
            'B': outputs['Fixnvdissol']['OUTPUT'],
            'SPLIT': True,
            'RESULT': parameters['Cicatrizes']
        }
        outputs['Diferena'] = processing.run('saga:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Cicatrizes'] = outputs['Diferena']['RESULT']
        return results

    def name(self):
        return '1-IdentificaQueimadas_22072021'

    def displayName(self):
        return '1-IdentificaQueimadas_22072021'

    def group(self):
        return 'Fire-Mirador-2021'

    def groupId(self):
        return 'Fire-Mirador-2021'

    def createInstance(self):
        return Identificaqueimadas_22072021()
