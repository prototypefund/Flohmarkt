import { fetchJSON } from "./utils.js";
import { getCurrentUser } from "./current_user.js";
import { createAvatar, createSmallAvatar } from "./create/avatar.js";

const [reportees, currentUser] = await Promise.all([
    fetchJSON('report/reportees'),
    getCurrentUser
])

const reportedItem = document.createElement('template');
reportedItem.innerHTML = `
    <link rel="stylesheet" href="/static/container.css">
    <style>
        .reported {
            border: 1px solid white;
            border-bottom:none;
            border-top-left-radius:10px;
            border-top-right-radius:10px;
        }
        .reports {
            border: 1px solid white;
            border-top:none;
            border-bottom-left-radius:10px;
            border-bottom-right-radius:10px;
        }
        .image {
            padding-left:10px;
            width:200px;
            height:150px;
        }
        .showbutton {
            margin-bottom:5px;
        }
    </style>
    <div class="row reported">
        <div class="col-md-3"><img class="image"><span class="name">item caption</span></div>
        <div class="col-md-3">
            <textarea> Please enter a reason here </textarea>
            <button> Suspend </button>
            <button> Delete </button>
        </div>
    </div>
    <div class="row reports">
        <button class="showbutton">Reports anzeigen</button>
    </div>
`;

class ReportedItem extends HTMLElement {
    constructor () {
        super();
        this._shadowRoot = this.attachShadow({mode:'open'});
        this._shadowRoot.appendChild(reportedItem.content.cloneNode(true));

        this.image = this._shadowRoot.querySelector('img');
        this.label = this._shadowRoot.querySelector('.name');
        this.reports = this._shadowRoot.querySelector('.reports');
    }

    setItem(val) {
        this.item = val;
        this.render();
        const showbutton = this.shadowRoot.querySelector('.showbutton');
        showbutton.addEventListener('click', async e => {
            const reports = await fetchJSON('report/'+this.item.id);
            this.reports.innerHTML = "";
            reports.forEach(report => {
                const e = document.createElement('report-card');
                e.setReport(report);
                this.reports.appendChild(e);
            });
        })
    }

    render () {
        this.image.src = "/api/v1/image/"+this.item.images[0];  
        this.label.innerHTML = this.item.name;
    }
}

window.customElements.define('reported-item', ReportedItem);

const reportedUser = document.createElement('template');
reportedUser.innerHTML = `
    <link rel="stylesheet" href="/static/container.css">
    <link rel="stylesheet" href="/static/user.css">
    <style>
        .reported {
            border-top-left-radius:10px;
            border-top-right-radius:10px;
            border: 1px solid white;
            border-bottom: none;
            height:150px;
        }
        .reports {
            border-bottom-left-radius:10px;
            border-bottom-right-radius:10px;
            border: 1px solid white;
            border-top: none;
        }
        .text {
            display:inline-block;
            height:150px;
        }
        .name {
            color: white;
        }
        .ava {
            display: inline-block;
            padding-left: 10px;
            width: 200px;
            text-align: center;
            margin-top:  10px;
        }
        .showbutton {
            margin-bottom:5px;
        }
    </style>
    <div class="row reported">
        <div class="col-md-3"><div class="ava"></div><span class="name">user caption</span></div>
        <div class="col-md-3">
            <textarea> Please enter a reason here </textarea>
            <button> Ban </button>
        </div>
    </div>
    <div class="row reports">
        <button class="showbutton">Reports anzeigen</button>
    </div>
`;

class ReportedUser extends HTMLElement {
    constructor () {
        super();
        this._shadowRoot = this.attachShadow({mode:'open'});
        this._shadowRoot.appendChild(reportedUser.content.cloneNode(true));

        this.avatar_container = this.shadowRoot.querySelector('.ava');
        this.label = this.shadowRoot.querySelector('.name');
        this.reports = this._shadowRoot.querySelector('.reports');
    }

    setUser(val) {
        this.user = val;
        this.render();
        const showbutton = this.shadowRoot.querySelector('.showbutton');
        showbutton.addEventListener('click', async e => {
            const reports = await fetchJSON('report/'+this.user.id);
            this.reports.innerHTML = "";
            reports.forEach(report => {
                const e = document.createElement('report-card');
                e.setReport(report);
                this.reports.appendChild(e);
            });
        })
    }

    render () {
        this.avatar_container.innerHTML = "";
        this.avatar_container.appendChild(createAvatar(this.user));
        this.label.innerHTML = this.user.name + "<br>" + this.user.bio;
    }
}
window.customElements.define('reported-user', ReportedUser);

const reportCard = document.createElement('template');
reportCard.innerHTML = `
    <link rel="stylesheet" href="/static/container.css">
    <link rel="stylesheet" href="/static/user.css">
    <style>
        .ava {
            display: inline-block;
            padding-left: 10px;
            width: 200px;
            text-align: center;
            margin-top:  10px;
        }
    </style>
    <div class="row report">
        <div class="col-md-3 ava"></div>
        <div class="col-md-3 userinfo"><span class="name"></span></div>
        <div class="col-md-3 text"><span class="content"></span></div>
    </div>
`;

class ReportCard extends HTMLElement {
    constructor () {
        super();
        this._shadowRoot = this.attachShadow({mode:'open'});
        this._shadowRoot.appendChild(reportCard.content.cloneNode(true));

        this.avatar_container = this.shadowRoot.querySelector('.ava');
        this.namedisplay = this.shadowRoot.querySelector('.name');
        this.reporttext = this.shadowRoot.querySelector('.text');
    }

    async setReport(val) {
        this.report = val;
        this.user = await fetchJSON('user/'+this.report.user_id);
        this.render();
    }

    render () {
        this.avatar_container.innerHTML = "";
        this.avatar_container.appendChild(createSmallAvatar(this.user));
        this.namedisplay.innerHTML = this.user.name;
        this.reporttext.innerHTML = this.report.reason;
    }
}

window.customElements.define('report-card', ReportCard);

const gridResults = document.querySelector('.col__reportees');

reportees.forEach( reportee =>  {
    let e = null;
    if (reportee.type === "item") {
        e = document.createElement('reported-item');
        e.setItem(reportee);
    } else if (reportee.type === "user") {
        e = document.createElement('reported-user');
        e.setUser(reportee);
    }
    
    gridResults.appendChild(e); 
})

