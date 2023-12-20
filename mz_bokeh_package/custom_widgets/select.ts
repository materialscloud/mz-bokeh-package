import {select} from "core/dom"
import {isString} from "core/util/types"
import * as p from "core/properties"

import {InputWidget, InputWidgetView} from "models/widgets/input_widget"

import {
  common_styles, 
  DropdownOption, 
  GroupedOptions,
  fix_collapsed_by_default,
} from "./select_widgets_common_components"

declare function $(...args: any[]): any

const default_styles = common_styles + `
  .multiselect-group.dropdown-item-text {
    padding-left: 10px;
  }
  label.form-check-label.single-select::before {
    border-radius: 50%;
  }
`;

export class CustomSelectView extends InputWidgetView {
  model: CustomSelect
  protected select_el: HTMLSelectElement
  protected options: any
  protected plugin_config: any
  protected all_values: Array<string|string[]>

  connect_signals(): void {
    super.connect_signals()

    const {value, options, name, title, enabled} = this.model.properties
    this.on_change([value, options, name, title], () => this.render())
    this.on_change(enabled, () => this.enable_widget())
  }

  styles(): string[] {
    return [...super.styles(), default_styles]
  }

  initialize(): void {
    super.initialize()
    super.render()

    this.select_el = this.init_select_element()
  }

  init_select_element(): HTMLSelectElement{
    // Create a "Select" web element
    const select_el = select({
      size: this.model.allow_non_selected ? 2 : 1,  // Allows none of the options to be selected
      class: "custom-select",
      name: this.model.name,
      style: "display: none;",
    })

    // Add the "Select" web element to its container 
    this.group_el.appendChild(select_el)

    return select_el
  }

  parse_options_list(options: Array<(string | string[])>): Array<DropdownOption> {
    return options.map((opt: any) => {
      let label: string, value: string, selected: boolean
      
      if(isString(opt)) {
        value = label = opt;
      } else {
        [value, label] = opt;
      }

      if (!this.model.value) {
        selected = false
      } else if (this.model.is_opt_grouped && this.model.value instanceof Array){
        /* Note! an assumption is made that the option's value is 
        unique across all other options (not only in its group) */
        selected = this.model.value[1] === value 
      } else {
        selected = isString(this.model.value) && this.model.value === value 
      }
      
      return {value, label, selected}
    })
  }

  // Build an "options" object based on "CustomMultiSelect" properties
  parse_options(): Array<DropdownOption | GroupedOptions> {
    // options are not grouped
    if(Array.isArray(this.model.options)) {
      this.model.is_opt_grouped = false
      const options = this.parse_options_list(this.model.options)
      this.all_values = options.map(opt => opt.value)
      return options
    }
    
    // options are grouped
    this.model.is_opt_grouped = true
    const options = Object.entries(this.model.options).map(([group, children]) => {
      return {
        label: group,
        children: this.parse_options_list(children)
      }
    })
    this.all_values = options.reduce((acc: any, {label: group, children}) => {
      return acc.concat(children.map((c: any) => [group, c.value]))
    }, [])
    return options
  }

  set_plugin_config(): any {
    const plugin_config = {
      maxHeight: 200,
      disableIfEmpty: true,
      nonSelectedText: this.model.non_selected_text,
      enableCaseInsensitiveFiltering: this.model.enable_filtering,
      buttonWidth: '100%',
      numberDisplayed: 1,
      onChange: this.on_dropdown_change.bind(this),
      onDropdownShown: this.on_dropdown_opened.bind(this),
      onDropdownHidden: this.on_dropdown_closed.bind(this),
      enableCollapsibleOptGroups: this.model.collapsible,
      collapseOptGroupsByDefault: this.model.collapsed_by_default,
    }

    if (this.model.width) {
      plugin_config.buttonWidth = `${this.model.width}px`
    }

    if (!this.model.collapsible) {
      plugin_config.collapseOptGroupsByDefault = false
    }

    return plugin_config
  }

  // Apply styles specifically for the current widget
  apply_unique_styles(): void {
    const root_el = $(this.group_el).parents('.bk-root')[0]
    const width = this.model.width ? `${this.model.width}px` : 'calc(100% - 4px)'
    const styles: {[key: string]: any} = {
      "> .bk.custom_select": {
        "width": width,
        "max-width": width,
      }
    }

    for (const selector in styles) {
      for (const property in styles[selector]) {
        $(selector, root_el).css(property, styles[selector][property])
      }
    }
  }

  apply_plugin(): void {
    this.options = this.parse_options()

    this.plugin_config = this.set_plugin_config()
    
    $(this.select_el).multiselect(this.plugin_config).multiselect('dataprovider', this.options).multiselect('rebuild')
  
    // fixes the scroll issue on mobile
    $('.multiselect-container.dropdown-menu', this.group_el).unbind('touchstart')

    // Add a class to differentiate between css rules
    $('label.form-check-label', this.group_el).addClass('single-select')

    this.apply_unique_styles()

    let is_non_selected: boolean
    if (this.model.is_opt_grouped) {
      is_non_selected = this.options.length ? this.options.every((group: any) => group.children.every((child: any) => !child.selected)) : true
    } else {
      is_non_selected = this.options.length ? this.options.every((opt: any) => !opt.selected) : true
    }
    
    // set the "value" property when "allow_non_selected" is set to False
    if (!this.model.allow_non_selected && is_non_selected && this.all_values.length) {
      const value = this.all_values[0]
      this.model.setv({value}, {silent: true})
    }

    // allow for deselecting and leaving the widget in the unselected state.
    const selected_button = $('button.multiselect-option.dropdown-item.active', this.group_el)
    if (this.model.allow_non_selected && selected_button.length)
      selected_button[0].onclick = this.deselect_option.bind(this)

    if (this.model.collapsed_by_default && this.model.collapsible)
      fix_collapsed_by_default(this.group_el)
  }

  render(): void {
    this.apply_plugin()

    // Enable/disable the widget in case it has options 
    // (if there are no options it is disabled automatically) 
    this.enable_widget()
  }

  enable_widget(): void {
    const hasOptions = (this.model.is_opt_grouped && this.options.some((opt: any) => opt.children.length)) || this.options.length
    
    if (hasOptions) {
      $(document).ready(() => $(this.select_el).multiselect(`${this.model.enabled ? 'enable' : 'disable'}`))
    }
  }

  // function to bind to selected item for allowing to deselect it again.
  // this function is called twice, but the python event is raised only once.
  deselect_option(): void {
    this.model.value = ""
    const dropdown_menu = $('div.multiselect-container.dropdown-menu', this.group_el)
    dropdown_menu.removeClass("show")
  }

  // Runs after a change occurs 
  on_dropdown_change(): void {
    if (this.model.allow_non_selected)
      return

    const selected = $('button.multiselect-option.dropdown-item.active', this.group_el)
    
    if (!selected.length) {
      $(this.select_el).multiselect('select', this.model.value).multiselect('refresh')
    }
  }

  // Runs after the drop-down is opened
  on_dropdown_opened(): void {
    const selected = $('button.multiselect-option.dropdown-item.active', this.group_el)
    
    if (selected.length) {
      const position = selected[0].offsetTop
      const dropdownMenu = $('.multiselect-container.dropdown-menu', this.group_el)
      const dropdownMenuHeight = dropdownMenu.outerHeight()
      dropdownMenu[0].scrollTo(0, position-dropdownMenuHeight/2)
    }
  }

  // Runs after the drop-down is closed
  on_dropdown_closed(): void {
    let value: string | string[]
    let was_value_changed: boolean
    const selectedValue = $(this.select_el).val() || ""

    if (this.model.is_opt_grouped) {
      value = this.all_values.find((v: any) => v[1] === selectedValue) || ""
      was_value_changed = !(this.model.value instanceof Array) || this.model.value[1] !== value[1]
    } else {
      value = selectedValue
      was_value_changed = this.model.value !== value
    }

    if (was_value_changed) {
      this.model.setv({value})
      super.change_input()
    }
  }
}

export namespace CustomSelect {
  export type Attrs = p.AttrsOf<Props>

  export type Props = InputWidget.Props & {
    value: p.Property<string | string[]>
    options: p.Property<({[key: string]: (string | string[])[]} | (string | string[])[])>
    enable_filtering: p.Property<boolean>
    enabled: p.Property<boolean>
    allow_non_selected: p.Property<boolean>
    non_selected_text: p.Property<string>
    is_opt_grouped: p.Property<boolean>
    collapsible: p.Property<boolean>
    collapsed_by_default: p.Property<boolean>
  }
}

export interface CustomSelect extends CustomSelect.Attrs {}

export class CustomSelect extends InputWidget {
  properties: CustomSelect.Props
  __view_type__: CustomSelectView

  constructor(attrs?: Partial<CustomSelect.Attrs>) {
    super(attrs)
  }

  static init_CustomSelect(): void {
    this.prototype.default_view = CustomSelectView

    this.define<CustomSelect.Props>(({String, Array, Tuple, Or, Boolean, Dict}) => ({
      value:                 [ Or(String, Array(String)), "" ],
      options:               [ Or(Dict(Array(Or(String, Tuple(String, String)))), Array(Or(String, Tuple(String, String)))), [] ],
      enable_filtering:      [ Boolean, false ],
      enabled:               [ Boolean, true ],
      allow_non_selected:    [ Boolean, true ],
      non_selected_text:     [ String, "Select..." ],
      is_opt_grouped:        [ Boolean, false ],
      collapsible:           [ Boolean, false ],
      collapsed_by_default:  [ Boolean, false ],
    }))
  }
}
