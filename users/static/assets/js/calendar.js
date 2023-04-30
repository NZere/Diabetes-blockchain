(function($) {
	"use strict";

	$(document).ready(function () {
    function c(passed_month, passed_year, calNum) {
      var calendar = calNum == 0 ? calendars.cal1 : calendars.cal2;
      makeWeek(calendar.weekline);
      calendar.datesBody.empty();
      var calMonthArray = makeMonthArray(passed_month, passed_year);
      var r = 0;
      var u = false;
      while (!u) {
        if (daysArray[r] == calMonthArray[0].weekday) {
          u = true
        } else {
          calendar.datesBody.append('<div class="blank"></div>');
          r++;
        }
      }
      for (var cell = 0; cell < 42 - r; cell++) {
        if (cell >= calMonthArray.length) {
            calendar.datesBody.append('<div class="blank"></div>');
        } else {
          var shownDate = calMonthArray[cell].day;
          var iter_date = new Date(passed_year, passed_month, shownDate);
          if (((shownDate != today.getDate() && passed_month == today.getMonth()) || passed_month != today.getMonth()) && iter_date < today) {
            var m = '<div class="past__date">';
          } else {
            var m = checkToday(iter_date) ? '<div class="today">' : "<div>";
          }
          calendar.datesBody.append(m + shownDate + "</div>");
        }
      }

      var color = "#000";
      calendar.calHeader.find("h2").text(i[passed_month] + " " + passed_year);
      calendar.weekline.find("div").css("color", color);
      calendar.datesBody.find(".today").css("color", "#000");

      var clicked = false;
      selectDates(selected);

      clickedElement = calendar.datesBody.find('div');
      clickedElement.on("click", function () {
        clicked = $(this);
        var whichCalendar = calendar.name;

        if (firstClick && secondClick) {
          thirdClicked = getClickedInfo(clicked, calendar);
          var firstClickDateObj = new Date(firstClicked.year, firstClicked.month, firstClicked.date);
        
          var secondClickDateObj = new Date(secondClicked.year, secondClicked.month, secondClicked.date);
        
          var thirdClickDateObj = new Date(thirdClicked.year, thirdClicked.month, thirdClicked.date);
        
          if (secondClickDateObj > thirdClickDateObj && thirdClickDateObj > firstClickDateObj) {
            secondClicked = thirdClicked;
            bothCals.find(".calendar__content").find("div").each(function () {
              $(this).removeClass("selected");
              // $('.send').addClass("hidden");
              // $('.time__select').addClass("hidden");

            });
            
            selected = {};
            selected[firstClicked.year] = {};
            selected[firstClicked.year][firstClicked.month] = [firstClicked.date];
            selected = addChosenDates(firstClicked, secondClicked, selected);
          } else {
            selected = {};
            firstClicked = [];
            secondClicked = [];
            firstClick = false;
            secondClick = false;
            bothCals.find(".calendar__content").find("div").each(function () {
              $(this).removeClass("selected");
              // $('.send').addClass("hidden");
              // $('.time__select').addClass("hidden");
            });
          }
        }

        if (!firstClick) {
          firstClick = true;
          firstClicked = getClickedInfo(clicked, calendar);
          selected[firstClicked.year] = {};
          selected[firstClicked.year][firstClicked.month] = [firstClicked.date];
        } else {
          secondClick = true;
          secondClicked = getClickedInfo(clicked, calendar);

          var firstClickDateObj = new Date(firstClicked.year, firstClicked.month, firstClicked.date);
          var secondClickDateObj = new Date(secondClicked.year, secondClicked.month, secondClicked.date);

          if (firstClickDateObj > secondClickDateObj) {
            var cachedClickedInfo = secondClicked;
            secondClicked = firstClicked;
            firstClicked = cachedClickedInfo;
            selected = {};
            selected[firstClicked.year] = {};
            selected[firstClicked.year][firstClicked.month] = [firstClicked.date];
          } else if (firstClickDateObj.getTime() == secondClickDateObj.getTime()) {
            selected = {};
            firstClicked = [];
            secondClicked = [];
            firstClick = false;
            secondClick = false;
            $(this).removeClass("selected");
            // $('.send').addClass("hidden");
            // $('.time__select').addClass("hidden");
          }
            selected = addChosenDates(firstClicked, secondClicked, selected);
        }
        selectDates(selected);
      });
    }

    function selectDates(selected) {
      if (!$.isEmptyObject(selected)) {
        var dateElements1 = datesBody1.find('div');
        var dateElements2 = datesBody2.find('div');

        function highlightDates(passed_year, passed_month, dateElements) {
          if (passed_year in selected && passed_month in selected[passed_year]) {
            var daysToCompare = selected[passed_year][passed_month];
            for (var d in daysToCompare) {
              dateElements.each(function (index) {
                if (parseInt($(this).text()) == daysToCompare[d]) {
                  $(this).addClass('selected');
                  
                  // $('.send').removeClass("hidden");
                }
              });
            }
          }
        }

        highlightDates(year, month, dateElements1);
        highlightDates(nextYear, nextMonth, dateElements2);
      }
    }

    function makeMonthArray(passed_month, passed_year) {
      var e = [];
      for (var r = 1; r < getDaysInMonth(passed_year, passed_month) + 1; r++) {
        e.push({
          day: r,
          weekday: daysArray[getWeekdayNum(passed_year, passed_month, r)]
        });
      }
      return e;
    }

    function makeWeek(week) {
      week.empty();
      for (var e = 0; e < 7; e++) {
        week.append("<div>" + daysArray[e].substring(0, 3) + "</div>")
      }
    }

    function getDaysInMonth(currentYear, currentMon) {
      return (new Date(currentYear, currentMon + 1, 0)).getDate();
    }

    function getWeekdayNum(e, t, n) {
      return (new Date(e, t, n)).getDay();
    }

    function checkToday(e) {
      var todayDate = today.getFullYear() + '/' + (today.getMonth() + 1) + '/' + today.getDate();
      var checkingDate = e.getFullYear() + '/' + (e.getMonth() + 1) + '/' + e.getDate();
      return todayDate == checkingDate;
    }

    function getAdjacentMonth(curr_month, curr_year, direction) {
      var theNextMonth;
      var theNextYear;
      if (direction == "next") {
        theNextMonth = (curr_month + 1) % 12;
        theNextYear = (curr_month == 11) ? curr_year + 1 : curr_year;
      } else {
        theNextMonth = (curr_month == 0) ? 11 : curr_month - 1;
        theNextYear = (curr_month == 0) ? curr_year - 1 : curr_year;
      }
      return [theNextMonth, theNextYear];
    }

    function b() {
      today = new Date;
      year = today.getFullYear();
      month = today.getMonth();
      var nextDates = getAdjacentMonth(month, year, "next");
      nextMonth = nextDates[0];
      nextYear = nextDates[1];
    }

    var e = 480;

    var today;
    var year, month, nextMonth, nextYear;

    var r = [];
    var i = [
      "January",
      "Feburary",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December"];
    var daysArray = [
      "Sunday",
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday"];

    var cal1 = $("#calendar-first");
    var calHeader1 = cal1.find(".calendar__header");
    var weekline1 = cal1.find(".calendar__weekdays");
    var datesBody1 = cal1.find(".calendar__content");

    var cal2 = $("#calendar-second");
    var calHeader2 = cal2.find(".calendar__header");
    var weekline2 = cal2.find(".calendar__weekdays");
    var datesBody2 = cal2.find(".calendar__content");

    var bothCals = $(".calendar");

    var switchButton = bothCals.find(".calendar__header").find('.switch__month');

    var calendars = {
      "cal1": {
        "name": "first",
        "calHeader": calHeader1,
        "weekline": weekline1,
        "datesBody": datesBody1
      },
      "cal2": {
        "name": "second",
        "calHeader": calHeader2,
        "weekline": weekline2,
        "datesBody": datesBody2
      }
    }

    var clickedElement;
    var firstClicked, secondClicked, thirdClicked;
    var firstClick = false;
    var secondClick = false;
    var selected = {};

    b();
    c(month, year, 0);
    c(nextMonth, nextYear, 1);
    switchButton.on("click", function () {
      var clicked = $(this);
      var generateCalendars = function (e) {
        var nextDatesFirst = getAdjacentMonth(month, year, e);
        var nextDatesSecond = getAdjacentMonth(nextMonth, nextYear, e);
        month = nextDatesFirst[0];
        year = nextDatesFirst[1];
        nextMonth = nextDatesSecond[0];
        nextYear = nextDatesSecond[1];

        c(month, year, 0);
        c(nextMonth, nextYear, 1);
      };

      if (clicked.attr("class").indexOf("left") != -1) {
        generateCalendars("previous");
      } else {
        generateCalendars("next");
      }
      
      clickedElement = bothCals.find(".calendar__content").find("div");
    });

    function getClickedInfo(element, calendar) {
      var clickedInfo = {};
      var clickedCalendar, clickedMonth, clickedYear;
      clickedCalendar = calendar.name;

      clickedMonth = clickedCalendar == "first" ? month : nextMonth;
      clickedYear = clickedCalendar == "first" ? year : nextYear;
      clickedInfo = {
        "calNum": clickedCalendar,
        "date": parseInt(element.text()),
        "month": clickedMonth,
        "year": clickedYear
      }
      return clickedInfo;
    }
  });
})(jQuery);