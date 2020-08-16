$(function() {
  const dataResourceUrl = $(".recordedlogs").data("url");
  loadDataResources(dataResourceUrl, $("#from").val(), $("#until").val());
});

function makeCategoryTable(data, nrows) {
  const $table = $("#categories_table");
  const $pagination = $("#categories_pag");

  const pages_resources_table = Math.ceil(data.length / nrows);

  const $tbody = $table.find("tbody");

  $tbody.html("");
  $pagination.html("");

  data.forEach((item, index) => {
    
    const display = index >= nrows ? 'style="display: none"' : "";

    let line = `<tr id='category_access_${index}' class='.category_access_table' ${display}>`;

    line = `${line}<td><a href='${item.link}'>${item.cat_name}</a></td>`;
    line = `${line}<td>${item.access}</td>`;
    line = `${line}</tr>`;
    
    $tbody.append(line);
  });

  $pagination.append("<li class='page-item previous'>&lt;</li>");

  [...Array(pages_resources_table).keys()].forEach(i => {
    const page = `<li class='page-item page-item-number' data-page=${i + 1}>${i + 1}</li>`;
    
      $pagination.append(page);
      if(i>9)
        $(`#categories_pag .page-item-number[data-page=${i+1}]`).hide();
  });

  $("#categories_pag .page-item-number[data-page=1]").addClass("active");

  $pagination.append("<li class='page-item next'>&gt;</li>");

  $("#categories_pag .page-item-number").click(e => {
    const page = $(e.target).data("page");
    const init = page * nrows - nrows;
    const end = page * nrows;

    $("#categories_pag .page-item-number").removeClass("active");
    $(e.target).addClass("active");

    $("#categories_pag .category_access").each((i, el) => {
      if (i >= init && i < end) {
        $(el).show();
      } else {
        $(el).hide();
      }
    });
  });

  $("#categories_pag .previous").click(() => {
    let page = $("#categories_pag .page-item-number.active").data("page");
    
    page = page === 1 ? 1 : page - 1;
    if(page>10){
      
      [...Array(pages_resources_table).keys()].forEach(i => {
        
        if(i<page+5 && i> page-5)
          $(`#categories_pag .page-item-number[data-page=${i+1}]`).show();
        });
    }
    else { 
      [...Array(pages_resources_table).keys()].forEach(i => {
        if(i>9)
            $(`#categories_pag .page-item-number[data-page=${i+1}]`).hide();
        else
        $(`#categories_pag .page-item-number[data-page=${i+1}]`).show();
      });

    }
    const init = page * nrows - nrows;
    const end = page * nrows;

    $("#categories_pag .page-item-number").removeClass("active");
    $(`#categories_pag .page-item-number[data-page=${page}]`).addClass("active");

    $("#categories_table .category_access").each((i, el) => {
      if (i >= init && i < end) {
        $(el).show();
      } else {
        $(el).hide();
      }
    });
  });

  $("#categories_pag .next").click(() => {
    let page = $("#categories_pag .page-item-number.active").data("page");
    
    page = page === pages_resources_table ? pages_resources_table : page + 1;
    if(page>10){
      
      [...Array(pages_resources_table).keys()].forEach(i => {
        
        if(i<page+5 && i> page-5)
          $(`#categories_pag .page-item-number[data-page=${i+1}]`).show();
        else if(i<pages_resources_table-9)
          $(`#categories_pag .page-item-number[data-page=${i+1}]`).hide();
      });

    }
    const init = page * nrows - nrows;
    const end = page * nrows;

    $("#categories_pag .page-item-number").removeClass("active");
    $(`#categories_pag .page-item-number[data-page=${page}]`).addClass("active");

    $("#categories_table .category_access").each((i, el) => {
      if (i >= init && i < end) {
        $(el).show();
      } else {
        $(el).hide();
      }
    });
  });
  $("#categories_table th.sort").off("click");
  $("#categories_table th.sort").on("click", el => {
    el.preventDefault();
    el.stopPropagation();

    const $el = $(el.target);
    const sort = $el.data("sort");
    const $icon = $($el.find("i"));
    const isAscending = $icon.hasClass("fa-sort-up");

    if (isAscending) {
      $("#categories_table th.sort i")
        .removeClass("fa-sort-up")
        .removeClass("fa-sort-down")
        .removeClass("fa-sort")
        .addClass("fa-sort");

      $icon.removeClass("fa-sort").addClass("fa-sort-down");

      if (sort === "name") {
        data.sort((a, b) => a.cat_name.localeCompare(b.cat_name)).reverse();

        makeCategoryTable(data, 10);
      } else {
        data.sort((a, b) => (a.access > b.access ? 1 : a.access < b.access ? -1 : 0)).reverse();

        makeCategoryTable(data, 10);
      }
    } else {
      $("#categories_table th.sort i")
        .removeClass("fa-sort-up")
        .removeClass("fa-sort-down")
        .removeClass("fa-sort")
        .addClass("fa-sort");

      $icon.removeClass("fa-sort").addClass("fa-sort-up");

      if (sort === "name") {
        data.sort((a, b) => a.cat_name.localeCompare(b.cat_name));

        makeCategoryTable(data, 10);
      } else {
        data.sort((a, b) => (a.access > b.access ? 1 : a.access < b.access ? -1 : 0));

        makeCategoryTable(data, 10);
      }
    }
  });
}
function makeSubjectsTable(data, nrows) {
  const $table = $("#subjects_table");
  const $pagination = $("#subjects_pag");

  const pages_subjects_table = Math.ceil(data.length / nrows);

  const $tbody = $table.find("tbody");

  $tbody.html("");
  $pagination.html("");

  data.forEach((item, index) => {
    
    const display = index >= nrows ? 'style="display: none"' : "";

    let line = `<tr id='subject_access_${index}' class='.subject_access_table' ${display}>`;

    
    line = `${line}<td><a href='${item.link}'>${item.name}</a></td>`;
    line = `${line}<td>${item.access}</td>`;
    line = `${line}</tr>`;
    
    $tbody.append(line);
  });
  
  $pagination.append("<li class='page-item previous'>&lt;</li>");

  [...Array(pages_subjects_table).keys()].forEach(i => {
    const page = `<li class='page-item page-item-number' data-page=${i + 1}>${i + 1}</li>`;
    
      $pagination.append(page);
      if(i>9)
        $(`#subjects_pag .page-item-number[data-page=${i+1}]`).hide();
  });

  $("#subjects_pag .page-item-number[data-page=1]").addClass("active");

  $pagination.append("<li class='page-item next'>&gt;</li>");

  $("#subjects_pag .page-item-number").click(e => {
    const page = $(e.target).data("page");
    const init = page * nrows - nrows;
    const end = page * nrows;

    $("#subjects_pag .page-item-number").removeClass("active");
    $(e.target).addClass("active");

    $("#subjects_table .subject_access_table").each((i, el) => {
      if (i >= init && i < end) {
        $(el).show();
      } else {
        $(el).hide();
      }
    });
  });

  $("#subjects_pag .previous").click(() => {
    let page = $("#subjects_pag .page-item-number.active").data("page");
    
    page = page === 1 ? 1 : page - 1;
    if(page>10){
      
      [...Array(pages_subjects_table).keys()].forEach(i => {
        
        if(i<page+5 && i> page-5)
          $(`#subjects_pag .page-item-number[data-page=${i+1}]`).show();
        });
    }
    else { 
      [...Array(pages_subjects_table).keys()].forEach(i => {
        if(i>9)
            $(`#subjects_pag .page-item-number[data-page=${i+1}]`).hide();
        else
        $(`#subjects_pag .page-item-number[data-page=${i+1}]`).show();
      });

    }
    const init = page * nrows - nrows;
    const end = page * nrows;

    $("#subjects_pag .page-item-number").removeClass("active");
    $(`#subjects_pag .page-item-number[data-page=${page}]`).addClass("active");

    $("#subjects_table .subject_access_table").each((i, el) => {
      if (i >= init && i < end) {
        $(el).show();
      } else {
        $(el).hide();
      }
    });
  });

  $("#subjects_pag .next").click(() => {
    let page = $("#subjects_pag .page-item-number.active").data("page");
    
    page = page === pages_subjects_table ? pages_subjects_table : page + 1;
    if(page>10){
      
      [...Array(pages_subjects_table).keys()].forEach(i => {
        
        if(i<page+5 && i> page-5)
          $(`#subjects_pag .page-item-number[data-page=${i+1}]`).show();
        else if(i<pages_subjects_table-9)
          $(`#subjects_pag .page-item-number[data-page=${i+1}]`).hide();
      });

    }
    const init = page * nrows - nrows;
    const end = page * nrows;

    $("#subjects_pag .page-item-number").removeClass("active");
    $(`#subjects_pag .page-item-number[data-page=${page}]`).addClass("active");

    $("#subjects_table .subject_access").each((i, el) => {
      if (i >= init && i < end) {
        $(el).show();
      } else {
        $(el).hide();
      }
    });
  });
  $("#subjects_table th.sort").off("click");
  $("#subjects_table th.sort").on("click", el => {
    el.preventDefault();
    el.stopPropagation();

    const $el = $(el.target);
    const sort = $el.data("sort");
    const $icon = $($el.find("i"));
    const isAscending = $icon.hasClass("fa-sort-up");

    if (isAscending) {
      $("#subjects_table th.sort i")
        .removeClass("fa-sort-up")
        .removeClass("fa-sort-down")
        .removeClass("fa-sort")
        .addClass("fa-sort");

      $icon.removeClass("fa-sort").addClass("fa-sort-down");

      if (sort === "name") {
        data.sort((a, b) => a.name.localeCompare(b.name)).reverse();

        makeSubjectsTable(data, 10);
      } else {
        data.sort((a, b) => (a.access > b.access ? 1 : a.access < b.access ? -1 : 0)).reverse();

        makeSubjectsTable(data, 10);
      }
    } else {
      $("#subjects_table th.sort i")
        .removeClass("fa-sort-up")
        .removeClass("fa-sort-down")
        .removeClass("fa-sort")
        .addClass("fa-sort");

      $icon.removeClass("fa-sort").addClass("fa-sort-up");

      if (sort === "name") {
        data.sort((a, b) => a.name.localeCompare(b.name));

        makeSubjectsTable(data, 10);
      } else {
        data.sort((a, b) => (a.access > b.access ? 1 : a.access < b.access ? -1 : 0));

        makeSubjectsTable(data, 10);
      }
    }
  });
}
function makeResourceTable(data, nrows) {
  const $table = $("#resources_table");
  const $pagination = $("#resources_pag");

  const pages_resources_table = Math.ceil(data.length / nrows);

  const $tbody = $table.find("tbody");

  $tbody.html("");
  $pagination.html("");

  data.forEach((item, index) => {
    
    const display = index >= nrows ? 'style="display: none"' : "";

    let line = `<tr id='resources_access_${index}' class='resource_access' ${display}>`;

    
    line = `${line}<td><a>${item.name}</a></td>`;
    line = `${line}<td>${item.access}</td>`;
    line = `${line}</tr>`;
    
    $tbody.append(line);
  });

  $pagination.append("<li class='page-item previous'>&lt;</li>");

  [...Array(pages_resources_table).keys()].forEach(i => {
    const page = `<li class='page-item page-item-number' data-page=${i + 1}>${i + 1}</li>`;
    
      $pagination.append(page);
      if(i>9)
        $(`#resources_pag .page-item-number[data-page=${i+1}]`).hide();
  });

  $("#resources_pag .page-item-number[data-page=1]").addClass("active");

  $pagination.append("<li class='page-item next'>&gt;</li>");

  $("#resources_pag .page-item-number").click(e => {
    const page = $(e.target).data("page");
    const init = page * nrows - nrows;
    const end = page * nrows;

    $("#resources_pag .page-item-number").removeClass("active");
    $(e.target).addClass("active");

    $("#resources_table .resource_access").each((i, el) => {
      if (i >= init && i < end) {
        $(el).show();
      } else {
        $(el).hide();
      }
    });
  });

  $("#resources_pag .previous").click(() => {
    let page = $("#resources_pag .page-item-number.active").data("page");
    
    page = page === 1 ? 1 : page - 1;
    if(page>10){
      
      [...Array(pages_resources_table).keys()].forEach(i => {
        
        if(i<page+5 && i> page-5)
          $(`#resources_pag .page-item-number[data-page=${i+1}]`).show();
        });
    }
    else { 
      [...Array(pages_resources_table).keys()].forEach(i => {
        if(i>9)
            $(`#resources_pag .page-item-number[data-page=${i+1}]`).hide();
        else
        $(`#resources_pag .page-item-number[data-page=${i+1}]`).show();
      });

    }
    const init = page * nrows - nrows;
    const end = page * nrows;

    $("#resources_pag .page-item-number").removeClass("active");
    $(`#resources_pag .page-item-number[data-page=${page}]`).addClass("active");

    $("#resources_table .resource_access").each((i, el) => {
      if (i >= init && i < end) {
        $(el).show();
      } else {
        $(el).hide();
      }
    });
  });

  $("#resources_pag .next").click(() => {
    let page = $("#resources_pag .page-item-number.active").data("page");
    
    page = page === pages_resources_table ? pages_resources_table : page + 1;
    if(page>10){
      
      [...Array(pages_resources_table).keys()].forEach(i => {
        
        if(i<page+5 && i> page-5)
          $(`#resources_pag .page-item-number[data-page=${i+1}]`).show();
        else if(i<pages_resources_table-9)
          $(`#resources_pag .page-item-number[data-page=${i+1}]`).hide();
      });

    }
    const init = page * nrows - nrows;
    const end = page * nrows;

    $("#resources_pag .page-item-number").removeClass("active");
    $(`#resources_pag .page-item-number[data-page=${page}]`).addClass("active");

    $("#resources_table .resource_access").each((i, el) => {
      if (i >= init && i < end) {
        $(el).show();
      } else {
        $(el).hide();
      }
    });
  });
  $("#resources_table th.sort").off("click");
  $("#resources_table th.sort").on("click", el => {
    
    el.preventDefault();
    el.stopPropagation();

    const $el = $(el.target);
    const sort = $el.data("sort");
    const $icon = $($el.find("i"));
    const isAscending = $icon.hasClass("fa-sort-up");

    if (isAscending) {
      $("#resources_table th.sort i")
        .removeClass("fa-sort-up")
        .removeClass("fa-sort-down")
        .removeClass("fa-sort")
        .addClass("fa-sort");

      $icon.removeClass("fa-sort").addClass("fa-sort-down");

      if (sort === "name") {
        data.sort((a, b) => a.name.localeCompare(b.name)).reverse();
        
        makeResourceTable(data, 10);
      } else {
        data.sort((a, b) => (a.access > b.access ? 1 : a.access < b.access ? -1 : 0)).reverse();
        
        makeResourceTable(data, 10);
      }
    } else {
      $("#resources_table th.sort i")
        .removeClass("fa-sort-up")
        .removeClass("fa-sort-down")
        .removeClass("fa-sort")
        .addClass("fa-sort");

      $icon.removeClass("fa-sort").addClass("fa-sort-up");

      if (sort === "name") {
        data.sort((a, b) => a.name.localeCompare(b.name));
        
        makeResourceTable(data, 10);
      } else {
        data.sort((a, b) => (a.access > b.access ? 1 : a.access < b.access ? -1 : 0));
        
        makeResourceTable(data, 10);
      }
    }
  });
  
}

function loadDataResources(url, dataIni, dataEnd) {
  $.get(url, { data_ini: dataIni, data_end: dataEnd }, dataset => {
    dataset.categories = dataset.categories.map(d => {
      d.value = d.access;
      
      return d;
    });
    dataset.subjects = dataset.subjects.map(d => {
      d.value = d.access;
      return d;
    });
    dataset.categories = dataset.categories.sort((d1, d2) => {
      return d1.value < d2.value ? 1 : d1.value > d2.value ? -1 : 0;
    });
    dataset.subjects = dataset.subjects.sort((d1, d2) => {
      return d1.value < d2.value ? 1 : d1.value > d2.value ? -1 : 0;
    });
    
    let reducedData = dataset.resources
    .reduce((sum,current) => {
        var found = false
        sum.forEach(function(row,i) {
            if (row.name === current.name) {
                sum[i].access += current.access
                found = true;
            }
        })
        if (found === false) sum.push(current)
        return sum
    }, []);
    
    reducedData = reducedData.sort((d1, d2) => {
      return d1.value < d2.access ? 1 : d1.access > d2.access ? -1 : 0;
    });

    console.log(reducedData);
    makeCategoryTable(dataset.categories, 10);
    makeSubjectsTable(dataset.subjects, 10);
    makeResourceTable(reducedData, 10);

  });
  
}
