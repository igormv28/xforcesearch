$("#loadingdiv").hide();
var table = $("#table").stonktable();

table.bind("aftertablesort", function(event, data) {
    var th = $(this).find("th");
    th.find(".arrow").remove();
    var arrow = data.direction === "asc" ? "Γåæ" : "Γåô";
    th.eq(data.column).append('<span class="arrow">' + arrow + "</span>");
});

$("#myInput").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#mytbody tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
});

$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
    $("#version")[0].value = "";
});

var checkBuild = function() {
    var unit = 5;
    var trs = $("#table").find("tr").length;
    if (trs == 1) {
        alert("Search first.");
    } else {
        var version = $("#version")[0].value;
        if (version != "") {
            var atag = $("a");
            var urls = 0;
            for (var i = 0; i < atag.length; i++) {
                if (atag[i].innerText.includes("http")) {
                    urls++;
                }
            }
            var delay = (unit * urls) / 60;
            delay = delay.toFixed(2);
            var check = confirm(
                "This search can take about " +
                delay +
                " minutes to page " +
                urls +
                " links. Confirm?"
            );
            if (check == true) {
                $('#inspectModal').modal('hide');
                $("#loadingdiv").show();
                $("form").submit();
            }
        }
    }
};

$("li").on("click", function() {
    var exPlatforms = $(this)[0].children[0].innerText;
    $("#platform").val(exPlatforms);
});
var doSearch = function() {
    $("#version").val("");
    if ($("#platform").val() != "") {
        $("#loadingdiv").show();
        $("form").submit();
        $("#buildsearchbtn")[0].removeAttribute("disabled");
    }
};

var hd_platform = $("#arr_platform").val();
if (hd_platform) {
    window.localStorage.setItem("arr_platform", hd_platform);
}

function sort_by_key(array, key) {
    return array.sort(function(a, b) {
        var x = a[key];
        var y = b[key];
        return ((x < y) ? -1 : ((x > y) ? 1 : 0));
    });
}

function autocomplete(inp, arr) {
    // console.log(arr.length);
    /*the autocomplete function takes two arguments,
            the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function(e) {
        var a,
            b,
            i,
            val = this.value.toUpperCase();
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (val.length < 2) {
            return false;
        }
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        var tmparr = [...arr];
        var arrval = val.split(" ");
        for (i = 0; i < arrval.length; i++) {
            var arrlen = tmparr.length;
            for (var j = arrlen - 1; j >= 0; j--) {
                if (val[i] != "") {
                    var arrj = tmparr[j].toUpperCase();
                    var vali = arrval[i].toUpperCase();
                    if (arrj.indexOf(vali) == -1) {
                        tmparr.splice(j, 1);
                    }
                }
            }
        }

        var trimval = val.trim();
        if (trimval == "") {
            tmparr = [];
        }
        // console.log(val);
        /*for each item in the array...*/
        for (i = 0; i < tmparr.length; i++) {
            /*create a DIV element for each matching element:*/
            b = document.createElement("DIV");

            if (arrval.length > 1) {
                // Remove empty item in array
                for (var j = arrval.length - 1; j >= 0; j--) {
                    if (arrval[j] == "") {
                        arrval.splice(j, 1);
                    }
                }
                arrval = [...new Set(arrval)];
                var tmp = [];
                for (var j = 0; j < arrval.length; j++) {
                    var checkflag = false;
                    for (var k = 0; k < arrval.length; k++) {
                        if (j != k) {
                            if (arrval[k].toUpperCase().indexOf(arrval[j].toUpperCase()) > -1) {
                                checkflag = true;
                            }
                        }
                    }
                    if (checkflag == false) {
                        tmp.push(arrval[j]);
                    }
                }
                arrval = tmp;

                // Sort arrval by index of the string
                tmp = [];

                for (var j = 0; j < arrval.length; j++) {
                    var idx = tmparr[i].toUpperCase().indexOf(arrval[j].toUpperCase());
                    tmp.push({ idx: idx, val: arrval[j] });
                }
                var resjson = sort_by_key(tmp, 'idx');
                arrval = [];
                for (var j = 0; j < resjson.length; j++) {
                    arrval.push(resjson[j]['val']);
                }
                // Write the string
                b.innerHTML += tmparr[i].substr(0, tmparr[i].toUpperCase().indexOf(arrval[0].toUpperCase()));
                b.innerHTML += "<strong style='color:blue;'>" + tmparr[i].substr(tmparr[i].toUpperCase().indexOf(arrval[0].toUpperCase()), arrval[0].length) + "</strong>";

                for (var j = 1; j < arrval.length; j++) {
                    b.innerHTML += tmparr[i].substring(tmparr[i].toUpperCase().indexOf(arrval[j - 1].toUpperCase()) + arrval[j - 1].length, tmparr[i].toUpperCase().indexOf(arrval[j].toUpperCase()));
                    b.innerHTML += "<strong style='color:blue;'>" + tmparr[i].substr(tmparr[i].toUpperCase().indexOf(arrval[j].toUpperCase()), arrval[j].length) + "</strong>";
                }

                b.innerHTML += tmparr[i].substr(tmparr[i].toUpperCase().indexOf(arrval[arrval.length - 1].toUpperCase()) + arrval[arrval.length - 1].length);
            } else if (arrval.length == 1) {
                b.innerHTML += tmparr[i].substr(0, tmparr[i].toUpperCase().indexOf(arrval[0].toUpperCase()));
                for (var j = 0; j < arrval.length; j++) {
                    b.innerHTML += "<strong style='color:blue;'>" + tmparr[i].substr(tmparr[i].toUpperCase().indexOf(arrval[0].toUpperCase()), arrval[0].length) + "</strong>";
                    b.innerHTML += tmparr[i].substr(tmparr[i].toUpperCase().indexOf(arrval[0].toUpperCase()) + arrval[0].length);
                }
            }
            /*insert a input field that will hold the current array item's value:*/
            b.innerHTML += "<input type='hidden' value='" + tmparr[i] + "'>";
            /*execute a function when someone clicks on the item value (DIV element):*/
            b.addEventListener("click", function(e) {
                /*insert the value for the autocomplete text field:*/
                inp.value = this.getElementsByTagName("input")[0].value;
                /*close the list of autocompleted values,
                            (or any other open lists of autocompleted values:*/
                closeAllLists();
            });
            a.appendChild(b);
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
                      increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 38) {
            //up
            /*If the arrow UP key is pressed,
                      decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
                /*and simulate a click on the "active" item:*/
                if (x) x[currentFocus].click();
            }
        }
    });

    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = x.length - 1;
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }

    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
                except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function(e) {
        closeAllLists(e.target);
    });
}
autocomplete(
    document.getElementById("platform"),
    window.localStorage.arr_platform.split("___")
);
