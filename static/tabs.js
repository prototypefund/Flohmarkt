const tabs = {}
const initialized = false;

export function initTabs() {
    document.querySelectorAll('.tabcontext').forEach( ctx => {
        ctx.querySelectorAll('.tab').forEach (tab => {
            if (tab.name == "") {
                return;
            }
            tab.addEventListener('click', event => {
                ctx.querySelectorAll('.tabpage').forEach (tabpage => {
                    if (tabpage.getAttribute("name") == tab.getAttribute("name")) {
                        tabpage.style.display = "block";
                    } else {
                        tabpage.style.display = "none";
                    }
                });
            });
        });
        ctx.querySelectorAll('.tabpage').forEach (tabpage => {
            if (tabpage.classList.contains("tab_default")) {
                tabpage.style.display = "block";
            }
        });
    });
}

