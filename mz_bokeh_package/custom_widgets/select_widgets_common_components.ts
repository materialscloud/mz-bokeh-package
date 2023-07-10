// styles that are common to both single and multi select widgets
export const common_styles = `
  /* Expand clickable area of the caret for collapsing groups */
  .custom_select .dropdown-toggle.caret-container {
    margin-left: -12px;
    padding: 7px 3px 8px 12px;
  }
  /* fix orientation of the open/close caret */
  .multiselect-container .multiselect-group.closed .dropdown-toggle::after {
    transform: none !important;
  }
  .dropdown-toggle.custom-select {
    font-size: inherit;
    display: flex;
    background: #fff url('data:image/svg+xml;utf8,<svg version="1.1" viewBox="0 0 25 20" xmlns="http://www.w3.org/2000/svg"><path d="M 0,0 25,0 12.5,20 Z" fill="black" /></svg>') no-repeat right 7px center/7px 10px;
  }
  .multiselect-container.dropdown-menu {
    width: inherit;
    overflow: auto auto !important;
  }
  .multiselect-option.dropdown-item {
    color: inherit;
    padding: 0 24px;
  }
  .multiselect-option.dropdown-item.active,
  .multiselect-option.dropdown-item:active {
    color: inherit;
    background-color: #FFFFFF;
  }
  .multiselect-option.dropdown-item:focus {
    outline: none;
  }
  .multiselect-group.dropdown-item-text {
    font-size: 13px;
  }
  .form-check-input {
    display: none;
  }
  .form-check-label {
    font-size: 13px;
  }
  .dropdown-item.active label.form-check-label::before {
    background-color: #60cbe0;
    border: 1px solid #60cbe0;
  }
  .dropdown-item.active label.form-check-label::after {
    display: block;
  }
  label.form-check-label::before {
    content: "";
    width: 14px;
    height: 14px;
    display: block;
    border: 1px solid currentColor;
    border-radius: 2px;
    box-sizing: border-box;
    left: -21px;
    top: calc(50% - 7px);
    position: absolute;
  }
  label.form-check-label {
    position: relative;
  }
  label.form-check-label::after {
    content: "";
    width: 5px;
    height: 8px;
    box-sizing: border-box;
    border-bottom: 2px solid white;
    border-right: 2px solid white;
    position: absolute;
    display: none;
    transform: rotate(45deg);
    left: -16px;
    top: calc(50% - 5px);
    z-index: 1;
  }
  div.input-group-prepend > svg.input-group-text {
    width: 30px !important;
    height: inherit !important;
  }
  .multiselect-filter {
    position: sticky;
    top: -6px;
    left: 0;
    right: 0;
    z-index: 2;
  }
  .multiselect-filter .input-group-prepend,
  .multiselect-filter .input-group-append {
    height: 31px;
  }
  span.multiselect-selected-text {
    width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    text-align: left;
  }
  span.multiselect-native-select {
    width: inherit;
  }
  .dropdown-item.active:hover {
    background-color: #f8f9fa;
  }
  .multiselect-clear-filter.input-group-text {
    outline: none;
  }
  `

export interface DropdownOption {
  value: string,
  label: string,
  selected: boolean,
}
export interface GroupedOptions {
  label: string,
  children: Array<DropdownOption>
}
