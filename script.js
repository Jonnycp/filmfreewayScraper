// ==UserScript==
// @name         FilmFreeway SCRAPER
// @namespace    jonnycp
// @version      2024-06-24
// @description  Ottieni i dati di tutti i recensori di un festival e scaricali in csv
// @author       Jonathan Caputo
// @match        https://filmfreeway.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=filmfreeway.com
// @grant        none
// ==/UserScript==

const scraper = async () => {
  console.log("SCRAPER attivo");
  let reviewSection = document.querySelector("section#reviews");
  if (reviewSection && reviewSection.dataset.reviewsSection) {
    let reviewsLink = reviewSection.dataset.reviewsSection;

    let nPage = 1;
    let reviewsAuthorLinks = [];
    while (nPage <= 2000) {
      let pageRecensori = await trovaRecensori(reviewsLink, nPage);
      if (pageRecensori[0] == "EXIT") {
        nPage = 2001;
      } else {
        reviewsAuthorLinks.push(...pageRecensori);
        nPage += 1;
      }
    }

    console.log(
      "Trovati",
      reviewsAuthorLinks.length,
      "autori da",
      window.location.href
    );
    console.log(reviewsAuthorLinks);
    reviewsAuthorLinks.forEach(aut => {
        let autObj = getInfoFromAuthor(aut);
        if(autObj){
          console.log(autObj)
        }
    })
  }
};

const trovaRecensori = async (reviewsLink, nPage) => {
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
        : "";
    let title = d_2.querySelector("div.Header-profileTitle")
        ? d_2.querySelector("div.Header-profileTitle").innerHTML
        : "";
    let bio = d_2.querySelector("div.Header-Profile-introCopy")
        ? d_2.querySelector("div.Header-Profile-introCopy").innerHTML
        : "";
    let email = d_2.querySelector("meta[itemprop='email']")
        ? d_2.querySelector("meta[itemprop='email']").content
        : "";
    let bd = d_2.querySelector("div[itemprop='birthDate']")
        ? d_2.querySelector("div[itemprop='birthDate']").content
        : "";
    let city = "";
    let labels = ["Current City", "Hometown", "Birth City"];
    for (let label of labels) {
        let labelElement = Array.from(
            document.querySelectorAll(".Grid .TextStyle-medium")
        ).find((el) => el.textContent === label);
        let cityElement = labelElement
            ? labelElement.parentElement.nextElementSibling
            : null;
        city = cityElement ? cityElement.textContent : null;

        if (city) break;
    }
    return {
        "name": nome.split(" ").slice(0, -1).join(" "),
        "lastName": nome.split(" ").slice(-1),
        "title": title,
        "bio": bio,
        "email": email,
        "birthday": bd,
        "city": city,
        "author": autoreLink,
        "festival": window.location.href
    };
};

document.addEventListener("readystatechange", () => setTimeout(scraper, 1000));
