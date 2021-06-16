import {label, input, span} from "core/dom"
import {Markup, MarkupView} from "models/widgets/markup"
import * as p from "core/properties"

declare function $(...args: any[]): any

const default_styles = `
/* The toggle-btn - the box around the slider */
.toggle-btn {
  position: relative;
  display: inline-block;
  width: 30px;
  height: 13px;
}

/* Hide default HTML checkbox */
.toggle-btn input {
  opacity: 0;
  width: 0;
  height: 0;
}

/* The slider */
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #B0AFAF;
  -webkit-transition: .15s;
  transition: .15s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 17px;
  width: 17px;
  left: 0px;
  bottom: -2px;
  background-color: #F1F1F1;
  -webkit-transition: .15s;
  -moz-transition: .15s;
  transition: .15s;
}

input:checked + .slider {
  background-color: #ABDAE0;
}

input:focus + .slider {
  box-shadow: 0 0 1px #a8ebf8f5;
}

input:checked + .slider:before {
  background-color: #00BCD4;
  -webkit-transform: translateX(14px);
  -ms-transform: translateX(14px);
  transform: translateX(14px);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
  border: none;
  box-shadow: 0 0 3px -1px;
}

.bk.toggle-container {
  display: flex !important;
  width: unset !important;
  align-items: center;
}

.bk.bk-clearfix.toggle-title {
  margin-right: 6px;
}
`

export class CustomToggleView extends MarkupView {
  model: CustomToggle
  protected toggle_btn: HTMLLabelElement

  styles(): string[] {
    return [...super.styles(), default_styles + this.model.styles]
  }

  initialize(): void {
    super.initialize()
    super.render()

    this.toggle_btn = this.init_toggle_btn()
  }

  init_toggle_btn(): HTMLLabelElement {
    const label_el = label({class: "toggle-btn"})
    const span_el = span({class: "slider round"})
    const input_el = input({class: "toggle-checkbox", type: "checkbox"})
    
    // Add "click" listener on the toggle-checkbox element to toggle "active" value
    input_el.addEventListener("click", this.toggle_active.bind(this))
    
    label_el.appendChild(input_el)
    label_el.appendChild(span_el)
    
    return label_el
  }

  render(): void {
    super.render()
    this.markup_el.textContent = this.model.text
    
    $(document).ready(this.on_document_ready.bind(this))
  }
  
  toggle_active(): void {
    setTimeout(() => {
      this.model.active = !this.model.active
    }, 200)
  }
  
  on_document_ready(): void {
    const toggle_container = $(this.markup_el).parent() 

    toggle_container.addClass('toggle-container')
    $(this.markup_el).addClass('toggle-title')
    
    // Set "checked" attribute of the checkbox based on "active" property
    $(".toggle-checkbox", this.toggle_btn).prop("checked", this.model.active);
    
    // Add the toggle button as a child of the toggle container
    toggle_container.append(this.toggle_btn)
  }
}

export namespace CustomToggle {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Markup.Props & {
    active: p.Property<boolean>
    styles: p.Property<string>
  }
}

export interface CustomToggle extends CustomToggle.Attrs {}

export class CustomToggle extends Markup {
  properties: CustomToggle.Props
  __view_type__: CustomToggleView

  constructor(attrs?: Partial<CustomToggle.Attrs>) {
    super(attrs)
  }

  static init_CustomToggle(): void {
    this.prototype.default_view = CustomToggleView

    this.define<CustomToggle.Props>(({Boolean, String}) => ({
      active: [ Boolean, false ],
      styles: [ String, '' ],
    }))
  }
}
