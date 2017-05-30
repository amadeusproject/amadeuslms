(function (b) {
    b(function () {
        b.widget("blk.hpaging", {
            options: { limit: 5, activePage: 1, parentID: "", navBar: null, totalPages: "" }, _create: function () { var a = this._getNavBar(); b(this.element).after(a) }, _getNavBar: function () { var a; a = b(this.element).prop("id"); this.options.parentID = a; a = b("<div id=pg_" + a + ">").addClass("pagination").data("parentID", a); this.options.navBar = a; this.setPages(this.options.activePage); return a }, clearPages: function () {
                b(this.options.navBar).empty(); b("#" + this.options.parentID + " > tbody > tr").show();
                b("#" + this.options.parentID + " > tbody > tr").removeData("page"); return !0
            }, newRow: function (a) { this.setPages(); var c = b("#" + this.options.parentID + " > tbody > tr"); a = b(c).eq(a).data("page"); this.activePage(a) }, newLimit: function (a) { this.options.limit = a; this.setPages() && this.activePage(1) }, setPages: function (a) {
                var c = !1; if (this.clearPages()) {
                    var c = this.options.limit, h = b("#" + this.options.parentID + " > tbody > tr"), f, d = h.length / c; f = d; d = d.toString().split("."); 2 == d.length && (f = parseInt(d[0]) + 1); 0 == f && (f = 1); d =
                        this.options.parentID; this._setPage(d, 1, "<<"); this._setPage(d, "P-1", "<"); for (var g = 0, k = c, e, l = 1; l <= f; l++)g = h.slice(g, k), e = l, b(g).removeData("page"), b(g).data("page", e), this._setPage(d, e, e), g = k, k = parseInt(k) + parseInt(c); this._setPage(d, "P+1", ">"); this._setPage(d, e, ">>"); this.options.totalPages = e; void 0 !== a && this.activePage(a); c = !0
                } return c
            }, _setPage: function (a, c, h) { a = b("<a>", { href: "#", text: h, "data-page": c }).appendTo(this.options.navBar); this._on(a, { click: "onPageClick" }) }, activePage: function (a) {
                var c =
                    1 * a; this.options.activePage = c; b("#" + this.options.parentID + " > tbody > tr").each(function () { b(this).data("page") == c ? b(this).show() : b(this).hide() }); this._selectActivePage()
            }, _selectActivePage: function () { var a = this.options.activePage; b(this.options.navBar).find("a").each(function () { var c = b(this).text(); b(this).data("page") == a && "<<" != c && ">>" != c && (b(this).attr("class", "active"), b(this).siblings().attr("class", "")) }) }, onPageClick: function (a) {
                a.preventDefault(); a = b(a.target).data("page"); "P-1" == a ? (a = this.options.activePage -
                    1, 1 > a && (a = 1)) : "P+1" == a && (a = this.options.activePage + 1, a > this.options.totalPages && (a = this.options.totalPages)); this.activePage(a)
            }
        })
    })
})(jQuery);