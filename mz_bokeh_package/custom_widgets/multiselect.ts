import {select} from "core/dom"
import {isString} from "core/util/types"
import * as p from "core/properties"

import {InputWidget, InputWidgetView} from "models/widgets/input_widget"

import {common_styles} from "./select_widgets_common_components"

declare function $(...args: any[]): any

const default_styles = common_styles + `
  .multiselect-group.dropdown-item,
  .multiselect-all.dropdown-item {
    padding-left: 10px;
  }
  .multiselect-all.dropdown-item {
    padding-bottom: 0;
  }
  button.multiselect-group.dropdown-item.active,
  button.multiselect-group.dropdown-item:active,
  .multiselect-all.dropdown-item.active,
  .multiselect-all.dropdown-item:active {
    background-color: #FFFFFF;
    color: inherit;
  }
  button.multiselect-group.dropdown-item:focus,
  .multiselect-all.dropdown-item:focus {
    outline: none;
  }
  button.multiselect-group.dropdown-item.active:hover {
    background-color: #f8f9fa;
  }
`;

interface DropdownOption {
  value: string,
  label: string,
  selected: boolean,
}
interface GroupedOptions {
  label: string,
  children: Array<DropdownOption>
}

export class CustomMultiSelectView extends InputWidgetView {
  model: CustomMultiSelect
  protected select_el: HTMLSelectElement
  protected should_select_all: Boolean = true
  protected options: any
  protected plugin_config: any
  protected all_values: Array<string> = []

  connect_signals(): void {
    super.connect_signals()

    const {value, options, name, title, enabled} = this.model.properties
    this.on_change(value, () => this.update_value())
    this.on_change([name, title], () => this.render())
    this.on_change(enabled, () => this.enable_widget())
    this.on_change(options, () => this.update_options())
  }

  styles(): string[] {
    return [...super.styles(), default_styles]
  }

  initialize(): void {
    super.initialize()
    super.render()

    this.select_el = this.init_select_element()
    
    // initialize "value" to empty list if "select_all" is false 
    if (!this.model.value && !this.model.select_all) {
      this.model.setv({value: []}, {silent: true})
    }
  }

  init_select_element(): HTMLSelectElement{
    // Create a "Select" web element
    const select_el = select({
      multiple: "multiple",
      class: "custom-multiselect",
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
      } else if (this.model.is_opt_grouped){
        /* Note! an assumption is made that the option's value is 
        unique across all other options (not only in its group) */
        selected = this.model.value.some((v: any) => v[1] === value) 
      } else {
        selected = this.model.value.includes(value) 
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
      selectAllText: 'Select All',
      selectAllValue: 'Select All',
      disableIfEmpty: true,
      nonSelectedText: this.model.non_selected_text,
      enableCollapsibleOptGroups: this.model.collapsible,
      collapseOptGroupsByDefault: this.model.collapsed_by_default,
      enableCaseInsensitiveFiltering: this.model.enable_filtering,
      numberDisplayed: this.model.number_displayed,
      buttonWidth: '100%',
      includeSelectAllOption: this.model.include_select_all,
      enableClickableOptGroups: true,
      onDropdownShown: this.on_dropdown_opened.bind(this),
      onDropdownHidden: this.on_dropdown_closed.bind(this),
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
    
    $(this.select_el).multiselect(this.plugin_config).multiselect('dataprovider', this.options).multiselect('refresh')
  
    // fixes the scroll issue on mobile
    $('.multiselect-container.dropdown-menu', this.group_el).unbind('touchstart')

    this.apply_unique_styles()

    /* adds a wrapper around dropdown items.
    this solves the issue that the dropdown items width doesn't 
    stretch when the dropdown overflows on the x axis */
    this.add_options_wrapper()
  }

  render(): void {
    this.apply_plugin()

    // Enable/disable the widget in case it has options 
    // (if there are no options it is disabled automatically) 
    this.enable_widget()

    // select the "Select All" option (if needed)
    this.select_all(true)
  } 
  
  enable_widget(): void {
    const hasOptions = (this.model.is_opt_grouped && this.options.some((opt: any) => opt.children.length)) || this.options.length
    
    if (hasOptions) {
      $(document).ready(() => $(this.select_el).multiselect(`${this.model.enabled ? 'enable' : 'disable'}`))
    }
  }

  // Runs after the drop-down is opened
  on_dropdown_opened(): void {
    const selected = $('button.multiselect-option.dropdown-item.active', this.group_el)
    
    if (!this.model.select_all && selected.length) {
      const position = selected[0].offsetTop
      const dropdownMenu = $('.multiselect-container.dropdown-menu', this.group_el)
      const dropdownMenuHeight = dropdownMenu.outerHeight()
      dropdownMenu[0].scrollTo(0, position-dropdownMenuHeight/2)
    }
  }

  // Runs after the drop-down is closed
  on_dropdown_closed(): void {
    this.model.setv({dropdown_closed: !this.model.dropdown_closed})
    
    setTimeout(() => {
      const new_value = this.get_selected_options()
      const new_select_all = new_value.length === this.all_values.length ? true : false 
  
      const was_value_changed = this.model.value && (new_value.length !== this.model.value.length || 
        this.model.value.some((el, i) => el !== new_value[i]))
      
      if (new_select_all !== this.model.select_all || was_value_changed) {
        this.model.setv({select_all: new_select_all, value: new_value})
      }
    }, 200)
  }

  select_all(is_silent: Boolean | undefined): void {
    if (this.model.select_all) {
      $(this.select_el).multiselect('selectAll', false).multiselect('refresh')
     
      this.model.setv({value: this.all_values}, {silent: is_silent ? true : false})
    }
  }

  update_value(): void {
    this.apply_plugin()

    if (this.model.value && this.model.value.length == 0) {
      this.model.setv({select_all: false}, {silent: true})
    }
  }

  update_options(): void {
    this.apply_plugin()

    this.select_all(true)
  }

  get_selected_options(): Array<string | string[]> {
    const selectedValues = $(this.select_el).val()
    if (this.model.is_opt_grouped) {
      return this.all_values.filter(v => selectedValues.includes(v[1]))
    } else {
      return selectedValues
    }
  }

  add_options_wrapper(): void {
    if (!$("#items-container", this.group_el).length) {
      $(document).ready(() => 
        $(".dropdown-item, .multiselect-group", this.group_el).wrapAll( "<div id=items-container style='width: max-content; min-width: 100%' />")
      )
    }
  }
}

export namespace CustomMultiSelect {
  export type Attrs = p.AttrsOf<Props>

  export type Props = InputWidget.Props & {
    value: p.Property<(string | string[])[] | null>
    options: p.Property<({[key: string]: (string | string[])[]} | (string | string[])[])>
    include_select_all: p.Property<boolean>
    select_all: p.Property<boolean>
    number_displayed: p.Property<Number>
    enable_filtering: p.Property<boolean>
    enabled: p.Property<boolean>
    non_selected_text: p.Property<string>
    is_opt_grouped: p.Property<boolean>
    dropdown_closed: p.Property<boolean>
    collapsible: p.Property<boolean>
    collapsed_by_default: p.Property<boolean>
  }
}

export interface CustomMultiSelect extends CustomMultiSelect.Attrs {}

export class CustomMultiSelect extends InputWidget {
  properties: CustomMultiSelect.Props
  __view_type__: CustomMultiSelectView

  constructor(attrs?: Partial<CustomMultiSelect.Attrs>) {
    super(attrs)
  }

  static init_CustomMultiSelect(): void {
    this.prototype.default_view = CustomMultiSelectView

    this.define<CustomMultiSelect.Props>(({String, Array, Tuple, Or, Boolean, Number, Nullable, Dict}) => ({
      value:                 [ Nullable(Array(Or(String, Array(String)))), null ],
      options:               [ Or(Dict(Array(Or(String, Tuple(String, String)))), Array(Or(String, Tuple(String, String)))), [] ],
      include_select_all:    [ Boolean, false ],
      select_all:            [ Boolean, false ],
      number_displayed:      [ Number, 1 ],
      enable_filtering:      [ Boolean, false ],
      enabled:               [ Boolean, true ],
      non_selected_text:     [ String, "Select..." ],
      is_opt_grouped:        [ Boolean, false ],
      dropdown_closed:       [ Boolean, false ],
      collapsible:           [ Boolean, false ],
      collapsed_by_default:  [ Boolean, false ],
    }))
  }
}
