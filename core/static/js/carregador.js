/* * Copyright 2008, 2009 UFPE - Universidade Federal de Pernambuco * * Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS *  * O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como * publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença. *  * Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes. *   * Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENCA.txt", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA. * *///Variáveis globaisvar _loadTimer	= setInterval(__loadAnima,18);
var _loadPos	= 0;
var _loadDir	= 2;
var _loadLen	= 0;//Anima a barra de progresso
function __loadAnima(){
	var elem = document.getElementById("barra_progresso");
	if(elem != null){
		if (_loadPos==0) _loadLen += _loadDir;
		if (_loadLen>32 || _loadPos>79) _loadPos += _loadDir;
		if (_loadPos>79) _loadLen -= _loadDir;
		if (_loadPos>79 && _loadLen==0) _loadPos=0;
		elem.style.left		= _loadPos;
		elem.style.width	= _loadLen;
	}
}//Esconde o carregador
function __loadEsconde(){
	this.clearInterval(_loadTimer);
	var objLoader				= document.getElementById("carregador_pai");
	objLoader.style.display		="none";
	objLoader.style.visibility	="hidden";
}