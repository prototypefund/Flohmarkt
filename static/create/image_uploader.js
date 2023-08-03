import { createImg } from "./img.js";
import { createElement } from "./element.js";

const uploaderImage = document.createElement('template');
uploaderImage.innerHTML = `
    <link rel="stylesheet" href="/static/container.css">
    <style>
        textarea {
            width:60%;
	    height:100px;
        }
    </style>
    <div class="row">
        <div class="col-md-12">
            <div class="image"></div>
            <textarea class="alttext" placeholder="Image description"></textarea>
        </div>
	<canvas class="compress_canvas" hidden></canvas>
    </div>
`;

class UploaderImage extends HTMLElement {
    constructor () {
        super();
        this._shadowRoot = this.attachShadow({mode:'open'});
        this._shadowRoot.appendChild(uploaderImage.content.cloneNode(true));

        this.image = this._shadowRoot.querySelector(".image");
        this.alttext = this._shadowRoot.querySelector(".alttext");
        this.image_id = "";
    }

    static get observedAttributes() {
        return ['max-width', 'max-height'];
    }

    attributeChangedCallback(name, oldVal, newVal) {
        this[name] = newVal;
    }

    getData () {
        const data = {
            "image_id": this.image_id,
            "description": this.alttext.value
        };
        return data;
    }

    setImage (file) {
        const fileReader = new FileReader();
        fileReader.onload = e => {
            let srcData = e.target.result;
            const image = createImg(srcData, file.name, 'd-block');
            const showImage = createImg(srcData, file.name, 'd-block');
            showImage.style.width="30%";
            showImage.style.float="left";
            this.image.appendChild(showImage);
            image.onload = () => {
                let width = image.width,
                    height = image.height,
                    resize;
            
                if (width > height) {
                    if (width > this["max-width"]) {
                        height *= this["max-width"] / width;
                        width = this["max-width"];
                        resize = true;
                    }
                } else {
                    if (height > this["max-height"]) {
                        width *= this["max-height"] / height;
                        height = this["max-height"];
                        resize = true;
                    }
		}
                if (resize) {
                    const canvas = this._shadowRoot.querySelector('.compress_canvas');
                    const context = canvas.getContext('2d');
                    
                    canvas.width = width;
                    canvas.height = height;
                    
                    context.drawImage(image, 0, 0, width, height);
                    srcData = canvas.toDataURL('image/*');
                }
                window.fetch('/api/v1/image/', {
                        method: "post",
                        headers: {
                            "Authorization": "Bearer "+window.sessionStorage.getItem("token")
                        },
                        body: srcData
                    }
                ).then(data=>data.json()
                ).then(id=>{
                    this.image_id = id;
                });
            }
        }
        fileReader.readAsDataURL(file);
    }
}

window.customElements.define('uploader-image', UploaderImage);


const uploader = document.createElement('template');
uploader.innerHTML = `
    <link rel="stylesheet" href="/static/container.css">
    <link rel="stylesheet" href="/static/icon.css">
    <link rel="stylesheet" href="/static/utils.css">
    <style>
    	.upbox {
		text-align:center;
		padding-bottom:16px;
	}
    </style>
    <div class="row">
        <div class="col-md-12 upbox">
            <label class="m-0 cursor-pointer upbtn" for="upload">
                <svg class="icon icon--photo-up" role="img" aria-hidden="true">
                    <use href="/static/sprite.svg#photo-up"></use>
                </svg>
            </label>
            <input type="file" name="upload" class="upload" accept="image/*" multiple hidden>
        </div>
    </div>
    <div class="row images">
    </div>
`;

class Uploader extends HTMLElement {
    constructor () {
        super();
        this._shadowRoot = this.attachShadow({mode:'open'});
        this._shadowRoot.appendChild(uploader.content.cloneNode(true));

        this.upbtn = this._shadowRoot.querySelector('.upbtn');
        this.imagesdiv = this._shadowRoot.querySelector('.images');

        this.upload = this._shadowRoot.querySelector('.upload');
        this.upload.addEventListener('change', this.processUpload.bind(this));

	this.upbtn.addEventListener('click', ()=>this.upload.click() );
        this.images = [];
    }

    processUpload(e) {
        for (const file of this.upload.files) {
            const images = this._shadowRoot.querySelector(".images");
            const image = createElement('uploader-image',null,'');
            images.appendChild(image);
            this.images.push(image);
            image.setImage(file);
            image["max-width"] = 1080;
            image["max-height"] = 720;
        }

    }

    getData () {
        const res = [];
        this.images.forEach(e=>{
            res.push(e.getData());
        });
        return res;
    }

    render () {
    }
}

window.customElements.define('uploader-element', Uploader);
