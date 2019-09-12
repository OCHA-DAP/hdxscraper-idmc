#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Unit tests for scrapername.

'''
import copy
from os.path import join

import pytest
from hdx.data.dataset import Dataset
from hdx.data.hdxobject import HDXError
from hdx.data.vocabulary import Vocabulary
from hdx.hdx_configuration import Configuration
from hdx.hdx_locations import Locations
from hdx.location.country import Country
from hdx.utilities.compare import assert_files_same
from hdx.utilities.downloader import DownloadError
from hdx.utilities.path import temp_dir

from idmc import generate_indicator_datasets_and_showcase, generate_country_dataset_and_showcase, generate_resource_view


class TestIDMC:
    afg_dataset = {'name': 'idmc-idp-data-for-afghanistan', 'title': 'Afghanistan - Internally displaced persons - IDPs', 'maintainer': '196196be-6037-4488-8b71-d786adf4c081',
                   'owner_org': '647d9d8c-4cac-4c33-b639-649aad1c2893', 'data_update_frequency': '365', 'subnational': '0',
                   'tags': [{'name': 'hxl', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'displacement', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'},
                   {'name': 'internally displaced persons - idp', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'violence and conflict', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}],
                   'groups': [{'name': 'afg'}], 'notes': "Description\n\nContains data from IDMC's [Global Internal Displacement Database](http://www.internal-displacement.org/database/displacement-data).",
                   'methodology_other': '', 'caveats': '', 'dataset_preview': 'resource_id', 'dataset_date': '01/01/2008-12/31/2018'}
    afg_resources = [{'dataset_preview_enabled': 'True', 'description': 'Internally displaced persons - IDPs for Afghanistan', 'format': 'csv', 'name': 'displacement_data', 'resource_type': 'file.upload', 'url_type': 'upload'},
                     {'dataset_preview_enabled': 'False', 'description': 'Internally displaced persons - IDPs (new displacement associated with disasters) for Afghanistan', 'format': 'csv', 'name': 'disaster_data', 'resource_type': 'file.upload', 'url_type': 'upload'}]

    @pytest.fixture(scope='function')
    def configuration(self):
        Configuration._create(hdx_read_only=True, user_agent='test',
                              project_config_yaml=join('tests', 'config', 'project_configuration.yml'))
        Locations.set_validlocations([{'name': 'afg', 'title': 'Afghanistan'}, {'name': 'tza', 'title': 'Tanzania'}, {'name': 'world', 'title': 'World'}])
        Country.countriesdata(use_live=False)
        Vocabulary._tags_dict = True
        Vocabulary._approved_vocabulary = {'tags': [{'name': 'hxl'}, {'name': 'violence and conflict'}, {'name': 'displacement'}, {'name': 'internally displaced persons - idp'}], 'id': '4e61d464-4943-4e97-973a-84673c1aaa87', 'name': 'approved'}

    @pytest.fixture(scope='function')
    def downloader(self):
        class Download:
            @staticmethod
            def download_tabular_key_value(url):
                if url == 'https://lala':
                    return {
                        'Indicator Name': 'Internally displaced persons - IDPs',
                        'Long definition': 'Description',
                        'Statistical concept and methodology': 'Methodology',
                        'Limitations and exceptions': 'Caveats'
                    }
                elif url == 'https://haha':
                    return {
                        'Indicator Name': 'Internally displaced persons - IDPs (new displacement associated with disasters)',
                        'Long definition': 'Description',
                        'Statistical concept and methodology': 'Methodology',
                        'Limitations and exceptions': 'Caveats'
                    }

            @staticmethod
            def download_file(url, folder, filename):
                if url == 'https://dada':
                    return join('tests', 'fixtures', 'idmc_displacement_all_dataset.xlsx')
                elif url == 'https://wawa':
                    return join('tests', 'fixtures', 'idmc_disaster_all_dataset.xlsx')

            @staticmethod
            def setup(url):
                if 'Afghanistan' in url:
                    return True
                elif 'Republic' in url:
                    raise DownloadError('Download Error!')
                elif 'Tanzania' in url:
                    return True

        return Download()

    def test_generate_datasets_and_showcase(self, configuration, downloader):
        with temp_dir('idmc') as folder:
# indicator dataset test
            displacement_url = Configuration.read()['displacement_url']
            disaster_url = Configuration.read()['disaster_url']
            endpoints = Configuration.read()['endpoints']
            tags = Configuration.read()['tags']
            datasets, showcase, headersdata, countriesdata = generate_indicator_datasets_and_showcase(
                displacement_url, disaster_url, downloader, folder, endpoints, tags)
            assert datasets == {'displacement_data': {'name': 'idmc-internally-displaced-persons-idps', 'title': 'Internally displaced persons - IDPs',
                                                      'maintainer': '196196be-6037-4488-8b71-d786adf4c081', 'owner_org': '647d9d8c-4cac-4c33-b639-649aad1c2893',
                                                      'data_update_frequency': '365', 'subnational': '0',
                                                      'tags': [{'name': 'hxl', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'displacement', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'},
                                                               {'name': 'internally displaced persons - idp', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'},
                                                               {'name': 'violence and conflict', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}],
                                                      'notes': "Description\n\nContains data from IDMC's [Global Internal Displacement Database](http://www.internal-displacement.org/database/displacement-data).",
                                                      'methodology_other': 'Methodology', 'caveats': 'Caveats', 'groups': [{'name': 'world'}], 'dataset_date': '01/01/2008-12/31/2018', 'dataset_preview': 'resource_id'},
                                'disaster_data': {'name': 'idmc-internally-displaced-persons-idps-new-displacement-associated-with-disasters', 'title': 'Internally displaced persons - IDPs (new displacement associated with disasters)',
                                                  'maintainer': '196196be-6037-4488-8b71-d786adf4c081', 'owner_org': '647d9d8c-4cac-4c33-b639-649aad1c2893',
                                                  'data_update_frequency': '365', 'subnational': '0',
                                                  'tags': [{'name': 'hxl', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'displacement', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'},
                                                           {'name': 'internally displaced persons - idp', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'},
                                                           {'name': 'violence and conflict', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}],
                                                  'notes': "Description\n\nContains data from IDMC's [Global Internal Displacement Database](http://www.internal-displacement.org/database/displacement-data).",
                                                  'methodology_other': 'Methodology', 'caveats': 'Caveats', 'groups': [{'name': 'world'}], 'dataset_date': '01/01/2008-12/31/2018', 'dataset_preview': 'resource_id'}}
            resources = datasets['displacement_data'].get_resources()
            assert resources == [{'dataset_preview_enabled': 'True', 'description': 'Internally displaced persons - IDPs', 'format': 'csv', 'name': 'displacement_data', 'resource_type': 'file.upload', 'url_type': 'upload'}]
            resource_name = '%s.%s' % (resources[0]['name'], resources[0]['format'])
            expected_file = join('tests', 'fixtures', resource_name)
            actual_file = join(folder, resource_name)
            assert_files_same(expected_file, actual_file)

            resources = datasets['disaster_data'].get_resources()
            resource_name = '%s.%s' % (resources[0]['name'], resources[0]['format'])
            expected_file = join('tests', 'fixtures', resource_name)
            actual_file = join(folder, resource_name)
            assert_files_same(expected_file, actual_file)

            assert resources == [{'dataset_preview_enabled': 'True', 'description': 'Internally displaced persons - IDPs (new displacement associated with disasters)', 'format': 'csv', 'name': 'disaster_data',
                                  'resource_type': 'file.upload', 'url_type': 'upload'}]
            assert showcase == {'image_url': 'http://www.internal-displacement.org/global-report/grid2018/img/ogimage.jpg', 'name': 'idmc-global-report-on-internal-displacement',
                                'notes': 'Click the image on the right to go to the IDMC Global Report on Internal Displacement',
                                'tags': [{'name': 'hxl', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'displacement', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'},
                                         {'name': 'internally displaced persons - idp', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'violence and conflict', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}],
                                'title': 'IDMC Global Report on Internal Displacement', 'url': 'http://www.internal-displacement.org/global-report/grid2018/'}
#  country datasets tests
            dataset, showcase, empty_col = generate_country_dataset_and_showcase(downloader, folder, headersdata, 'AFG', countriesdata['AFG'], datasets, tags)
            assert dataset == TestIDMC.afg_dataset
            resources = dataset.get_resources()
            assert resources == [{'dataset_preview_enabled': 'True', 'description': 'Internally displaced persons - IDPs for Afghanistan', 'format': 'csv', 'name': 'displacement_data', 'resource_type': 'file.upload', 'url_type': 'upload'},
                                 {'dataset_preview_enabled': 'False', 'description': 'Internally displaced persons - IDPs (new displacement associated with disasters) for Afghanistan', 'format': 'csv', 'name': 'disaster_data', 'resource_type': 'file.upload', 'url_type': 'upload'}]
            resource_name = '%s.%s' % (resources[0]['name'], resources[0]['format'])
            expected_file = join('tests', 'fixtures', resource_name)
            actual_file = join(folder, resource_name)
            assert_files_same(expected_file, actual_file)
            resource_name = '%s.%s' % (resources[1]['name'], resources[1]['format'])
            expected_file = join('tests', 'fixtures', resource_name)
            actual_file = join(folder, resource_name)
            assert_files_same(expected_file, actual_file)

            assert showcase == {'name': 'idmc-idp-data-for-afghanistan-showcase', 'title': 'IDMC Afghanistan Summary Page', 'notes': 'Click the image on the right to go to the IDMC summary page for the Afghanistan dataset',
                                'url': 'http://www.internal-displacement.org/countries/Afghanistan/', 'image_url': 'http://www.internal-displacement.org/sites/default/files/logo_0.png',
                                'tags': [{'name': 'hxl', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'displacement', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'},
                                         {'name': 'internally displaced persons - idp', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'violence and conflict', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}]}
            assert empty_col == [False, False, False]

            dataset, showcase, empty_col = generate_country_dataset_and_showcase(downloader, folder, headersdata, 'TZA', countriesdata['TZA'], datasets, tags)
            assert dataset == {'name': 'idmc-idp-data-for-united-republic-of-tanzania', 'title': 'United Republic of Tanzania - Internally displaced persons - IDPs', 'maintainer': '196196be-6037-4488-8b71-d786adf4c081',
                               'owner_org': '647d9d8c-4cac-4c33-b639-649aad1c2893', 'data_update_frequency': '365', 'subnational': '0',
                               'tags': [{'name': 'hxl', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'displacement', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'},
                                        {'name': 'internally displaced persons - idp', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'violence and conflict', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}],
                               'groups': [{'name': 'tza'}], 'notes': "Description\n\nContains data from IDMC's [Global Internal Displacement Database](http://www.internal-displacement.org/database/displacement-data).",
                               'methodology_other': '', 'caveats': '', 'dataset_preview': 'resource_id', 'dataset_date': '01/01/2011-12/31/2012'}
            resources = dataset.get_resources()
            assert resources == [{'dataset_preview_enabled': 'True', 'description': 'Internally displaced persons - IDPs for United Republic of Tanzania', 'format': 'csv', 'name': 'displacement_data', 'resource_type': 'file.upload', 'url_type': 'upload'},
                                 {'dataset_preview_enabled': 'False', 'description': 'Internally displaced persons - IDPs (new displacement associated with disasters) for United Republic of Tanzania', 'format': 'csv', 'name': 'disaster_data', 'resource_type': 'file.upload', 'url_type': 'upload'}]
            resource_name = '%s.%s' % (resources[0]['name'], resources[0]['format'])
            expected_file = join('tests', 'fixtures', resource_name)
            actual_file = join(folder, resource_name)
            assert_files_same(expected_file, actual_file)
            resource_name = '%s.%s' % (resources[1]['name'], resources[1]['format'])
            expected_file = join('tests', 'fixtures', resource_name)
            actual_file = join(folder, resource_name)
            assert_files_same(expected_file, actual_file)

            assert showcase == {'name': 'idmc-idp-data-for-united-republic-of-tanzania-showcase', 'title': 'IDMC United Republic of Tanzania Summary Page', 'notes': 'Click the image on the right to go to the IDMC summary page for the United Republic of Tanzania dataset',
                                'url': 'http://www.internal-displacement.org/countries/Tanzania/', 'image_url': 'http://www.internal-displacement.org/sites/default/files/logo_0.png',
                                'tags': [{'name': 'hxl', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'displacement', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'},
                                         {'name': 'internally displaced persons - idp', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'violence and conflict', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}]}
            assert empty_col == [True, True, False]

            dataset, showcase, empty_col = generate_country_dataset_and_showcase(downloader, folder, headersdata, 'AB9', countriesdata['AB9'], datasets, tags)
            assert dataset is None
            assert showcase is None
            assert empty_col is None

    def test_generate_resource_view(self, configuration):
        dataset = Dataset(TestIDMC.afg_dataset)
        resources = copy.deepcopy(TestIDMC.afg_resources)
        resources[0]['id'] = '123'
        resources[0]['url'] = 'http://sasa/file1.csv'
        resources[1]['url'] = 'http://sasa/file2.csv'
        dataset.add_update_resources(resources)
        result = generate_resource_view(dataset)
        assert result == {'resource_id': '123', 'description': '', 'title': 'Quick Charts', 'view_type': 'hdx_hxl_preview',
                          'hxl_preview_config': '{"configVersion":5,"bites":[{"tempShowSaveCancelButtons":false,"ingredient":{"aggregateColumn":null,"valueColumn":"#affected+idps+ind+stock+conflict","aggregateFunction":"sum","dateColumn":"#date+year","comparisonValueColumn":null,"comparisonOperator":null,"filters":{},"description":""},"type":"timeseries","errorMsg":null,"computedProperties":{"explainedFiltersMap":{"remove empty valued rows":{"filterWith":[{"#affected+idps+ind+stock+conflict":"is not empty"}],"filterWithout":[]}},"pieChart":false,"title":"Sum of Conflict Stock Displacement by Year","dataTitle":"Conflict Stock Displacement"},"uiProperties":{"swapAxis":true,"showGrid":true,"color":"#0077ce","sortingByValue1":"DESC","sortingByCategory1":null,"showPoints":true,"internalColorPattern":["#1ebfb3","#0077ce","#f2645a","#9C27B0"],"title":"Conflict Stock Displacement each Year"},"dataProperties":{},"displayCategory":"Timeseries","hashCode":20811871},{"tempShowSaveCancelButtons":false,"ingredient":{"aggregateColumn":null,"valueColumn":"#affected+idps+ind+newdisp+conflict","aggregateFunction":"sum","dateColumn":"#date+year","comparisonValueColumn":null,"comparisonOperator":null,"filters":{},"description":""},"type":"timeseries","errorMsg":null,"computedProperties":{"explainedFiltersMap":{"remove empty valued rows":{"filterWith":[{"#affected+idps+ind+newdisp+conflict":"is not empty"}],"filterWithout":[]}},"pieChart":false,"title":"Sum of Conflict New Displacements by Year","dataTitle":"Conflict New Displacements"},"uiProperties":{"swapAxis":true,"showGrid":true,"color":"#0077ce","sortingByValue1":"DESC","sortingByCategory1":null,"showPoints":true,"internalColorPattern":["#1ebfb3","#0077ce","#f2645a","#9C27B0"],"title":"Conflict New Displacements each Year"},"dataProperties":{},"displayCategory":"Timeseries","hashCode":-1843090317},{"tempShowSaveCancelButtons":false,"ingredient":{"aggregateColumn":null,"valueColumn":"#affected+idps+ind+newdisp+disaster","aggregateFunction":"sum","dateColumn":"#date+year","comparisonValueColumn":null,"comparisonOperator":null,"filters":{},"description":""},"type":"timeseries","errorMsg":null,"computedProperties":{"explainedFiltersMap":{"remove empty valued rows":{"filterWith":[{"#affected+idps+ind+newdisp+disaster":"is not empty"}],"filterWithout":[]}},"pieChart":false,"title":"Sum of Disaster New Displacements by Year","dataTitle":"Disaster New Displacements"},"uiProperties":{"swapAxis":true,"showGrid":true,"color":"#0077ce","sortingByValue1":"DESC","sortingByCategory1":null,"showPoints":true,"internalColorPattern":["#1ebfb3","#0077ce","#f2645a","#9C27B0"],"title":"Disaster New Displacements each Year"},"dataProperties":{},"displayCategory":"Timeseries","hashCode":1805077698}],"cookbookName":"generic"}'}
        result = generate_resource_view(dataset, empty_col=[False, False, True])
        assert result == {'resource_id': '123', 'description': '', 'title': 'Quick Charts', 'view_type': 'hdx_hxl_preview',
                          'hxl_preview_config': '{"configVersion": 5, "bites": [{"tempShowSaveCancelButtons": false, "ingredient": {"aggregateColumn": null, "valueColumn": "#affected+idps+ind+stock+conflict", "aggregateFunction": "sum", "dateColumn": "#date+year", "comparisonValueColumn": null, "comparisonOperator": null, "filters": {}, "description": ""}, "type": "timeseries", "errorMsg": null, "computedProperties": {"explainedFiltersMap": {"remove empty valued rows": {"filterWith": [{"#affected+idps+ind+stock+conflict": "is not empty"}], "filterWithout": []}}, "pieChart": false, "title": "Sum of Conflict Stock Displacement by Year", "dataTitle": "Conflict Stock Displacement"}, "uiProperties": {"swapAxis": true, "showGrid": true, "color": "#0077ce", "sortingByValue1": "DESC", "sortingByCategory1": null, "showPoints": true, "internalColorPattern": ["#1ebfb3", "#0077ce", "#f2645a", "#9C27B0"], "title": "Conflict Stock Displacement each Year"}, "dataProperties": {}, "displayCategory": "Timeseries", "hashCode": 20811871}, {"tempShowSaveCancelButtons": false, "ingredient": {"aggregateColumn": null, "valueColumn": "#affected+idps+ind+newdisp+conflict", "aggregateFunction": "sum", "dateColumn": "#date+year", "comparisonValueColumn": null, "comparisonOperator": null, "filters": {}, "description": ""}, "type": "timeseries", "errorMsg": null, "computedProperties": {"explainedFiltersMap": {"remove empty valued rows": {"filterWith": [{"#affected+idps+ind+newdisp+conflict": "is not empty"}], "filterWithout": []}}, "pieChart": false, "title": "Sum of Conflict New Displacements by Year", "dataTitle": "Conflict New Displacements"}, "uiProperties": {"swapAxis": true, "showGrid": true, "color": "#0077ce", "sortingByValue1": "DESC", "sortingByCategory1": null, "showPoints": true, "internalColorPattern": ["#1ebfb3", "#0077ce", "#f2645a", "#9C27B0"], "title": "Conflict New Displacements each Year"}, "dataProperties": {}, "displayCategory": "Timeseries", "hashCode": -1843090317}], "cookbookName": "generic"}'}
