""" 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""
##
# Handles all communication with the database
##
from django.db import connection

from h5p.models import h5p_libraries

class H5PEditorStorage:
    ##
    # Decides which content types the editor should have
    ##
    def getLibraries(self, libraries=None):
        if libraries != None:
            librariesWithDetails = list()
            for library in libraries:
                details = h5p_libraries.objects.filter(machine_name=library['name'], major_version=library[
                                                    'majorVersion'], minor_version=library['minorVersion']).values('title', 'runnable', 'restricted', 'tutorial_url')
                if len(details) > 0:
                    details = details[0]
                    library['tutorialUrl'] = details['tutorial_url']
                    library['title'] = details['title']
                    library['runnable'] = details['runnable']
                    library['restricted'] = True if details[
                        'restricted'] == 1 else False
                    librariesWithDetails.append(library)

            return librariesWithDetails

        libraries = list()
        librariesResult = h5p_libraries.objects.filter(runnable=1, semantics__isnull=False).extra(select={'name': 'machine_name', 'majorVersion': 'major_version', 'minorVersion': 'minor_version', 'tutorialUrl': 'tutorial_url'}).values(
            'name', 'title', 'majorVersion', 'minorVersion', 'tutorialUrl', 'restricted').order_by('title')
        for library in librariesResult:
            libraries.append(library)

        return libraries

    ##
    # Load language file(JSON) from database.
    # This is used to translate the editor fields(title, description, etc...)
    ##
    def getLanguage(self, machineName, majorVersion, minorVersion, language):
        # Load translation field from DB
        cursor = connection.cursor()
        cursor.execute("""
			SELECT hlt.language_json
			FROM h5p_libraries_languages hlt
			JOIN h5p_libraries hl ON hl.library_id = hlt.library_id
			WHERE hl.machine_name = %s AND hl.major_version = %s AND hl.minor_version = %s AND hlt.language_code = %s
			""" % ("'" + machineName + "'", majorVersion, minorVersion, "'" + language + "'"))

        result = self.dictfetchall(cursor)
        return result[0]['language_json'] if len(result) > 0 else False

    ##
    # Returns all rows from a cursor as a dict
    ##
    def dictfetchall(self, cursor):
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
