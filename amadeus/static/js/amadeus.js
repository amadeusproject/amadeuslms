/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

var Amadeus = {
    /**
     * Set up page
     */
    setup: function(callback) {
        // run callback Function (if exsists)
        if (callback) callback();

        // set environment variables
        Amadeus.setEnvVars(function() {
            // import templates
            Amadeus.importTemplates(function() {
                // set up the navbar
                Amadeus.setUpNavbar();

                // set environment variables for templates
                Amadeus.setUpMain();
            });
        });
    },
    /**
     * Path related variables and functions
     */
    paths: {
        // application host
        host: window.location.protocol + '//' + window.location.host,
        // application resolved host
        resolveHost: function() {
            return window.location.href.split(/\/html\//g)[0] || Amadeus.paths.host;
        },
        // assets path
        assets: function(path) {
            base = Amadeus.paths.resolveHost() + '/assets';
            if (path) {
                return base + path;
            } else {
                return base;
            }
        },
        // components path
        components: function(path) {
            base = Amadeus.paths.resolveHost() + '/html/components';
            if (path) {
                return base + path;
            } else {
                return base;
            }
        },
        // screens path
        screens: function(path) {
            base = Amadeus.paths.resolveHost() + '/html/screens';
            if (path) {
                return base + path;
            } else {
                return base;
            }
        },
        // templates path
        templates: function(path) {
            base = Amadeus.paths.resolveHost() + '/html/templates';
            if (path) {
                return base + path;
            } else {
                return base;
            }
        },
        // default paths
        defaults: function() {
            return {
                templatePath: Amadeus.paths.templates(),
                hostPath: Amadeus.paths.resolveHost(),
                assetPath: Amadeus.paths.assets(),
                screenPath: Amadeus.paths.screens(),
                componentPath: Amadeus.paths.components(),
                controllerPath: Amadeus.paths.assets('/js/controllers')
            }
        }
    },
    /**
     * Util funcitions
     */
    utils: {
        /**
         * Function responsible to load an Array of files in chain
         */
        progressiveLoad: function(lst, func, callback) {
            if (lst instanceof Array) {
                if (lst.length > 1) {
                    func(lst[0], function(){
                        lst.shift();
                        Amadeus.utils.progressiveLoad(lst, func, callback);
                    });
                } else if (lst.length === 1) {
                    func(lst[0], callback || function(){});
                } else {
                    callback();
                }
            } else {
                if (callback) {
                    callback();
                }
            }
        },
        /**
         * load a script into head
         */
        loadScript: function(url, callback) {
            // Adding the script tag to the head as suggested before
            var head = document.getElementsByTagName('head')[0];
            var script = document.createElement('script');
            script.type = 'text/javascript';
            script.src = url;
            script.onload = callback;

            // Fire the loading
            head.appendChild(script);
        },
        /**
         * Function responsible to fetch stylesheets
         */
        loadStyle: function(url, callback) {
            // Adding the script tag to the head as suggested before
            var head = document.getElementsByTagName('head')[0];
            var style = document.createElement('link');
            style.rel = 'stylesheet';
            style.type = 'text/css';
            style.href = url;

            // Then bind the event to the callback function.
            // There are several events for cross browser compatibility.
            //style.onreadystatechange = callback;
            style.onload = callback;

            // Fire the loading
            head.appendChild(style);
        }
    },
    /**
     * Import HTML templates using w3data library
     */
    importTemplates: function(callback) {
        w3IncludeHTML();
        if (callback) callback();
    },
    /**
     * Set location in breadcrumb
     */
    setBreadcrumb: function(inactive, active) {
        setTimeout(function() {
            w3DisplayData('breadcrumb', { 'active': active, inactive: inactive });

            if (inactive === null) {
              $('#breadcrumb').addClass('no-inactive');
            }
        }, Amadeus.default.delay || 500);
    },
    /**
     * Set Up the system navbar
     */
    setUpNavbar: function(callback) {
        setTimeout(function() {
            w3DisplayData('navbar', Amadeus.paths.defaults());
            if (callback) callback();
        }, Amadeus.default.delay || 500);
    },
    /**
     * Set Up the system main content env variables
     */
    setUpMain: function(callback) {
        setTimeout(function() {
            w3DisplayData('main', Amadeus.paths.defaults());
            if (callback) callback();
        }, Amadeus.default.delay || 500);
    },
    /**
     * Set up needed environment vars
     */
    setEnvVars: function(callback) {
        w3DisplayData('body', Amadeus.paths.defaults());
        if (callback) callback();
    },
    /**
     * load controller custom scrips if exsists
     */
    loadControllers: function(callback) {
        scripts = document.getElementsByTagName('script');
        for (i = 0; i < scripts.length; i++) {
            if (scripts[i].src.indexOf(Amadeus.paths.assets('/js/controllers')) >= 0) {
                Amadeus.utils.progressiveLoad([scripts[i].src], Amadeus.utils.loadScript);
                parent = scripts[i].parentNode;
                parent.removeChild(scripts[i]);
            }
        }
        if (callback) callback();
    },
    /**
     * Responsible to load necessary assets
     */
    load: function(callback) {
        settings = Amadeus.paths.resolveHost() + '/settings.js'
        with (Amadeus.utils) {
            progressiveLoad([settings], loadScript, function() {
                if (Amadeus.default) {
                    progressiveLoad(Amadeus.default.scripts || [], loadScript, function() {
                        progressiveLoad(Amadeus.default.styles || [], loadStyle, function() {
                            Amadeus.setup(function() {
                                if (callback) callback();
                                setTimeout(function() {
                                    $.material.init();
                                    Amadeus.loadControllers();
                                    progressiveLoad([Amadeus.paths.assets('/js/main.js')], loadScript);
                                }, Amadeus.default.delay * 2 || 1000);
                            });
                        });
                    });
                }
            });
        }
    }
};

