/**
 * LocalMindAI のページ共通の言語切り替え。
 *
 * 各ページは言語ごとに <section data-lang="xx" data-page-title="..."> を持ち、
 * このスクリプトが 1 つだけを表示する。対応言語はアプリ本体（CFBundleLocalizations）と同じ。
 * JavaScript が無効なときは CSS 側で英語の節だけが表示される。
 */
(function () {
    "use strict";

    var SUPPORTED = [
        ["ja", "日本語"],
        ["en", "English"],
        ["zh-Hans", "简体中文"],
        ["zh-Hant", "繁體中文"],
        ["ko", "한국어"],
        ["es", "Español"],
        ["fr", "Français"],
        ["de", "Deutsch"],
        ["pt-BR", "Português (Brasil)"],
        ["it", "Italiano"]
    ];
    var FALLBACK = "en";
    var STORAGE_KEY = "localmindai-lang";

    document.documentElement.classList.remove("no-js");

    function sections() {
        return Array.prototype.slice.call(document.querySelectorAll("section[data-lang]"));
    }

    function availableCodes() {
        var present = sections().map(function (el) { return el.getAttribute("data-lang"); });
        return SUPPORTED.filter(function (item) { return present.indexOf(item[0]) !== -1; });
    }

    function mapChinese(lower) {
        if (lower.indexOf("zh-hant") === 0 || lower.indexOf("zh-tw") === 0 ||
            lower.indexOf("zh-hk") === 0 || lower.indexOf("zh-mo") === 0) {
            return "zh-Hant";
        }
        if (lower.indexOf("zh") === 0) return "zh-Hans";
        return null;
    }

    /** 希望する言語タグの並びから、このページにある言語を 1 つ選ぶ。 */
    function matchedSupported(preferred, codes) {
        var sorted = codes.map(function (item) { return item[0]; })
            .sort(function (a, b) { return b.length - a.length; });
        for (var i = 0; i < preferred.length; i++) {
            var tag = String(preferred[i] || "").replace(/_/g, "-");
            var lower = tag.toLowerCase();
            for (var j = 0; j < sorted.length; j++) {
                var code = sorted[j];
                if (lower === code.toLowerCase()) return code;
                if (lower.indexOf(code.toLowerCase() + "-") === 0) return code;
            }
            var zh = mapChinese(lower);
            if (zh && sorted.indexOf(zh) !== -1) return zh;
            // 地域違い（pt-PT → pt-BR など）は同じ言語の節に寄せる
            var base = lower.split("-")[0];
            for (var k = 0; k < sorted.length; k++) {
                if (sorted[k].toLowerCase().split("-")[0] === base) return sorted[k];
            }
        }
        return sorted.indexOf(FALLBACK) !== -1 ? FALLBACK : sorted[0];
    }

    function queryLang(codes) {
        var raw = new URLSearchParams(window.location.search).get("lang");
        return raw ? matchedSupported([raw], codes) : null;
    }

    function savedLang(codes) {
        try {
            var saved = localStorage.getItem(STORAGE_KEY);
            return saved ? matchedSupported([saved], codes) : null;
        } catch (e) {
            return null;
        }
    }

    function browserLang(codes) {
        var preferred = [];
        if (navigator.languages && navigator.languages.length) {
            preferred = Array.prototype.slice.call(navigator.languages);
        } else if (navigator.language) {
            preferred = [navigator.language];
        }
        return matchedSupported(preferred, codes);
    }

    function apply(code) {
        document.documentElement.lang = code;
        sections().forEach(function (el) {
            el.classList.toggle("is-active", el.getAttribute("data-lang") === code);
        });
        var active = document.querySelector('section[data-lang="' + code + '"]');
        if (active) {
            var title = active.getAttribute("data-page-title");
            if (title) document.title = title;
            var description = active.getAttribute("data-page-description");
            var meta = document.querySelector('meta[name="description"]');
            if (meta && description) meta.setAttribute("content", description);
        }
        // サイト内リンクは選んだ言語を引き継ぐ
        document.querySelectorAll("[data-lang-href]").forEach(function (el) {
            el.setAttribute("href", el.getAttribute("data-lang-href") + "?lang=" + encodeURIComponent(code));
        });
        var select = document.getElementById("lang-select");
        if (select) select.value = code;
    }

    function persist(code) {
        try {
            localStorage.setItem(STORAGE_KEY, code);
        } catch (e) {
            /* プライベートブラウズなどで保存できないときは記憶しない */
        }
        var url = new URL(window.location.href);
        url.searchParams.set("lang", code);
        history.replaceState(null, "", url);
    }

    var codes = availableCodes();
    if (!codes.length) return;

    var select = document.getElementById("lang-select");
    if (select) {
        codes.forEach(function (item) {
            var option = document.createElement("option");
            option.value = item[0];
            option.textContent = item[1];
            select.appendChild(option);
        });
        select.addEventListener("change", function () {
            apply(select.value);
            persist(select.value);
        });
    }

    apply(queryLang(codes) || savedLang(codes) || browserLang(codes));
})();
