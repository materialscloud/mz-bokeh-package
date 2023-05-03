import {select} from "core/dom"
import {isString} from "core/util/types"
import * as p from "core/properties"

import {InputWidget, InputWidgetView} from "models/widgets/input_widget"

import {common_styles, DropdownOption, GroupedOptions} from "./select_widgets_common_components"

declare function $(...args: any[]): any

const default_styles = common_styles + `
  .multiselect-group.dropdown-item-text {
    padding-left: 10px;
  }
  label.form-check-label.single-select::before {
    border-radius: 50%;
  }
`;

export class CustomMultiSelectAsSingleSelectView extends InputWidgetView {
  model: CustomMultiSelectAsSingleSelect
  protected select_el: HTMLSelectElement
  protected options: any
  protected plugin_config: any
  protected all_values: Array<string> = []
  protected last_selection: any

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
  }

  init_select_element(): HTMLSelectElement{
    // Create a "Select" web element
    const select_el = select({
      multiple: "multiple",
      size: 2,
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
      } else if (this.model.is_opt_grouped){
        /* Note! an assumption is made that the option's value is 
        unique across all other options (not only in its group) */
        selected = this.model.value[1] === value
      } else {
        selected = this.model.value.includes(value) 
      }
      
      return {value, label, selected}
    })
  }

  // Build an "options" object based on "CustomMultiSelectAsSingleSelect" properties
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
      allow_non_selected: this.model.allow_non_selected,
      nonSelectedText: this.model.non_selected_text,
      enableCollapsibleOptGroups: this.model.collapsible,
      collapseOptGroupsByDefault: this.model.collapsed_by_default,
      enableCaseInsensitiveFiltering: this.model.enable_filtering,
      buttonWidth: '100%',
      enableClickableOptGroups: false,
      onChange: this.on_dropdown_change.bind(this),
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

    // Add a class to differentiate between css rules
    $('label.form-check-label', this.group_el).addClass('single-select')

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
  }

  enable_widget(): void {
    const hasOptions = (this.model.is_opt_grouped && this.options.some((opt: any) => opt.children.length)) || this.options.length
    
    if (hasOptions) {
      $(document).ready(() => $(this.select_el).multiselect(`${this.model.enabled ? 'enable' : 'disable'}`))
    }
  }

  // Runs after a change occurs
  on_dropdown_change(): void {
    console.log("on_dropdown_change   ***************************")
    console.log(this.model.value)
    debugger;
    if (this.model.allow_non_selected)
      return

    const selected = $('button.multiselect-option.dropdown-item.active', this.group_el);
    console.log(selected);
    console.log(selected.length);
    console.log("this             : ", this);
    console.log("this.select_el   : ", this.select_el);
    console.log("this.group_el    : ", this.group_el);
    console.log("this.model.value : ", this.model.value);
    console.log("$(this.select_el): ", $(this.select_el));
    debugger;

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

    console.log("on_dropdown_closed   *********************************");
    console.log("selectedValue : ", selectedValue);
    debugger;

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

  update_value(): void {
    this.apply_plugin()

    if (this.model.value && this.model.value.length == 0) {
      this.model.setv({select_all: false}, {silent: true})
    }
  }

  update_options(): void {
    this.apply_plugin()
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

export namespace CustomMultiSelectAsSingleSelect {
  export type Attrs = p.AttrsOf<Props>

  export type Props = InputWidget.Props & {
    value: p.Property<string | string[]>
    options: p.Property<({[key: string]: (string | string[])[]} | (string | string[])[])>
    enable_filtering: p.Property<boolean>
    enabled: p.Property<boolean>
    allow_non_selected: p.Property<boolean>
    non_selected_text: p.Property<string>
    is_opt_grouped: p.Property<boolean>
    dropdown_closed: p.Property<boolean>
    collapsible: p.Property<boolean>
    collapsed_by_default: p.Property<boolean>
  }
}

export interface CustomMultiSelectAsSingleSelect extends CustomMultiSelectAsSingleSelect.Attrs {}

export class CustomMultiSelectAsSingleSelect extends InputWidget {
  properties: CustomMultiSelectAsSingleSelect.Props
  __view_type__: CustomMultiSelectAsSingleSelectView

  constructor(attrs?: Partial<CustomMultiSelectAsSingleSelect.Attrs>) {
    super(attrs)
  }

  static init_CustomMultiSelectAsSingleSelect(): void {
    this.prototype.default_view = CustomMultiSelectAsSingleSelectView

    this.define<CustomMultiSelectAsSingleSelect.Props>(({String, Array, Tuple, Or, Boolean, Dict}) => ({
      value:                 [ Or(String, Array(String)), "" ],
      options:               [ Or(Dict(Array(Or(String, Tuple(String, String)))), Array(Or(String, Tuple(String, String)))), [] ],
      enable_filtering:      [ Boolean, false ],
      enabled:               [ Boolean, true ],
      allow_non_selected:    [ Boolean, true ],
      non_selected_text:     [ String, "Select..." ],
      is_opt_grouped:        [ Boolean, false ],
      dropdown_closed:       [ Boolean, false ],
      collapsible:           [ Boolean, false ],
      collapsed_by_default:  [ Boolean, false ],
    }))
  }
}
