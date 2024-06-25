// ==UserScript==
// @name         FilmFreeway SCRAPER
// @namespace    jonnycp
// @version      1.0
// @description  Ottieni i dati di tutti i recensori di un festival e scaricali in csv
// @author       Jonathan Caputo
// @match        https://filmfreeway.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=filmfreeway.com
// @grant        none
// ==/UserScript==

const MAX_REVIEWS = 2000;

const scraper = async () => {
  let reviewSection = document.querySelector("section#reviews");
  if (reviewSection && reviewSection.dataset.reviewsSection) {
    //INIZIO
    console.log("SCRAPER attivo");
    let btn = document.querySelector(
      "section#reviews .reviews-component span a"
    );
    btn.innerHTML = "Caricamento...";

    //ID FESTIVAL
    let reviewsLink = reviewSection.dataset.reviewsSection;

    // TROVA LINK AI RECENSORI
    let nPage = 1;
    let reviewsAuthorLinks = [];
    while (nPage <= MAX_REVIEWS) {
      let pageRecensori = await findRecensori(reviewsLink, nPage);
      if (pageRecensori[0] == "EXIT") {
        nPage = MAX_REVIEWS + 1;
      } else {
        reviewsAuthorLinks.push(...pageRecensori);
        nPage += 1;
      }
    }

    //ANALISI AUTORI
    let emoji = reviewsAuthorLinks.length >= 1 ? "😁" : "😥";
    document.querySelector(
      "section#reviews div.reviews-component span.active.tab"
    ).innerHTML = reviewsAuthorLinks.length + " recensori trovati " + emoji;
    btn.innerHTML = "Ottenendo dati...";

    let autori = [];
    reviewsAuthorLinks.forEach(async (aut) => {
      let autObj = await getInfoFromAuthor(aut);
      if (autObj) {
        autori.push(autObj);
      }

      //DOWNLOAD
      if (autori.length == reviewsAuthorLinks.length) {
        toCSVDownload(autori);
        btn.innerHTML = "Fatto 😎";
      }
    });
  }
};

const findRecensori = async (reviewsLink, nPage) => {
  const d = await fetch(reviewsLink + "?page=" + nPage);
  const d_1 = await d.json();
  const d_2 = document.createRange().createContextualFragment(d_1.success);
  const rev = d_2.querySelectorAll("div.review-item__author");
  let pageRecensori = [];
  if (rev.length != 0) {
    rev.forEach((r) => {
      let aTag = r.querySelector("a");
      if (aTag && aTag.getAttribute("href")) {
        if (!pageRecensori.includes(aTag.getAttribute("href"))) {
          pageRecensori.push(aTag.getAttribute("href"));
        }
      }
    });
  } else {
    pageRecensori = ["EXIT"];
  }
  return pageRecensori;
};

const getInfoFromAuthor = async (linkAuthor) => {
  const d = await fetch(linkAuthor);
  const d_1 = await d.text();
  const d_2 = document.createRange().createContextualFragment(d_1);
  let nome = d_2.querySelector("div.Header-profileName")
    ? d_2.querySelector("div.Header-profileName").innerHTML
    : ".";
  let title = d_2.querySelector("div.Header-profileTitle")
    ? d_2.querySelector("div.Header-profileTitle").innerHTML
    : ".";
  let bio = d_2.querySelector("div.Profile-introCopy")
    ? d_2.querySelector("div.Profile-introCopy").innerHTML
    : ".";
  let email = d_2.querySelector("meta[itemprop='email']")
    ? d_2.querySelector("meta[itemprop='email']").content
    : ".";
  let bd = d_2.querySelector("div[itemprop='birthDate']")
    ? d_2.querySelector("div[itemprop='birthDate']").innerHTML
    : ".";
  let city = ".";
  let labels = ["Current City", "Hometown", "Birth City"];
  for (let label of labels) {
    let labelElement = Array.from(
        d_2.querySelectorAll(".Grid .TextStyle-medium")
    ).find((el) => el.textContent === label);
    let cityElement = labelElement
      ? labelElement.parentElement.nextElementSibling
      : null;
    city = cityElement ? cityElement.textContent : ".";

    if (city != ".") break;
  }

  return {
    name: nome.split(" ").slice(0, -1).join(" "),
    lastName: nome.split(" ").slice(-1).join(" "),
    email: email,
    title: title || ".",
    city: city,
    bio: bio || ".",
    birthday: bd,
    author: "https://filmfreeway.com"+linkAuthor,
    festival: window.location.href,
  };
};

const addButtonScraper = () => {
  let container = document.querySelector(
    "section#reviews .reviews-component span"
  );
  let span = document.createElement("span");
  let btn = document.createElement("a");
  let classes = [
    "btn",
    "btn-h4",
    "btn-white",
    "header-action",
    "pull-right",
    "hidden-xs",
    "ProfileFestival-ratingsInHeaderButton",
  ];
  classes.forEach((c) => btn.classList.add(c));
  btn.innerText = "Scarica autori";
  btn.addEventListener("click", scraper);
  span.appendChild(btn);
  if (container) {
    container.insertAdjacentElement("afterend", span);
    container.remove();
  }
};

const toCSVDownload = (data) => {
  let csvContent = "";
  let header = [
    "Nome",
    "Cognome",
    "Email",
    "Titolo",
    "Citta",
    "Bio",
    "Compleanno",
    "Link",
    "Festival",
  ];
  csvContent += header.join("=") + "\n";

  for (let row of data) {
    let values = Object.values(row);
    if(values[2] != "."){
        values[5] = values[5].replace(/\n/g, ""); 
        csvContent += values.join("=") + "\n";
    }
  }

  let blob = new Blob([csvContent], { type: "text/csv" });
  let url = URL.createObjectURL(blob);

  let a = document.createElement("a");
  a.href = url;
  let festival = window.location.href.split("/");
  a.download = "Recensori festival " + festival[festival.length - 1] + ".csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  URL.revokeObjectURL(url);
};

document.addEventListener("readystatechange", addButtonScraper);
