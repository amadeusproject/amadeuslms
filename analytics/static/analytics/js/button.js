/** 
 * Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 * 
 * Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 * 
 * O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 * 
 * Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 * 
 * Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/ 

var button_counter = 0
class Button{
    constructor(config){

    }
    static validData(config,this_config){
        this.create(Button.validData(config)).draw();
    }
    create(config){
        var a = this;
        this.config = config;

        return this;
    }
    draw(){
        var a = this;

        return this;
    }
    remove(){
        var a = this;

        return this;
    }
    redraw(config){
        this.config = Button.validData(config,this.config);
        this.draw();
        return this;
    }
}