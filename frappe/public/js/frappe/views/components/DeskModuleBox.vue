<template>
  <div
    v-if="!hidden"
    class="module-box"
    :class="{ 'hovered-box': hovered, 'blue': index % 2 == 0 }"
	:data-module-name="module_name"
  >
    <div class="module-box-content">
      <div :class="{'module-box-tabs': true, 'links-visible': showLinks}" >
        <div class="module-box-tab icon-tab">
          <i :class="icon_class" style="font-size:5em;"></i>
        </div>
        <div class="module-box-tab link-tab">
          <LinkTab v-if="dropdown_links && dropdown_links.length" :items="dropdown_links" />
          
        </div>
      </div>
    </div>
    <div class="module-box-footer">
        <a class="module-box-link" :href="type === 'module' ? '#modules/' + module_name : link">
          <div class='label'>{{ label }}</div>    
        </a>
        <div class="controls">
            <div :class="{indicator: true, active: !showLinks}"  @click="toggle_tab"></div>
            <div :class="{indicator: true, active: showLinks}"  @click="toggle_tab"></div>
        </div>
    </div>
  </div>
</template>

<script>

import LinkTab from "./LinkTabBox.vue";

export default {
  props: [
    "index",
    "name",
    "label",
    "category",
    "type",
    "module_name",
    "link",
    "count",
    "onboard_present",
    "links",
    "description",
    "hidden",
    "icon"
  ],
  components: {
    LinkTab
  },
  data() {
    return {
      hovered: 0,
      showLinks: false
    };
  },
  computed: {
    icon_class() {
      if (this.icon) {
        return this.icon;
      } else {
        return "octicon octicon-file-text";
      }
	},
  
	dropdown_links() {
		return this.type === 'module' ? this.links
			.filter(link => !link.hidden)
			.concat([
				{ label: __('Customize'), action: () => this.$emit('customize'), class: 'border-top' }
			]) : [];
	}
  },
  methods: {
    toggle_tab() {
      console.log('toggled');
      this.showLinks = !this.showLinks;
    }
  },
};
</script>

<style lang="less" scoped>
@import "frappe/public/less/variables";

.blue {
  background-color: #bbe1fa !important;
}

.blue .list-group-item {
  background: transparent;
}

.module-box {
  flex: 1;
  margin: 8px;
  height: 200px;
  min-width: 250px;
  box-shadow: 0px 0px 8px rgba(0,0,0,0.3);
  padding: 8px;
  background-color:white;
  color: #0f4c75;
  font-size: 20px;
  font-weight: 500;
  display:flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.module-box-content {
  flex: 1;
  width: 100%;
  overflow-x: hidden;


.links-visible {
  left: -100%;
}


  p {
    margin-top: 5px;
    font-size: 80%;
    display: flex;
    overflow: hidden;
  }
}

.module-box-tabs {
    display: flex;
    width:200%;
    height:100%;
    position: relative;
    left: 0px;
    transition: all 0.5s linear
}

.module-box-tab {
  width: 100%;
}

.icon-tab {
  display:flex;
  justify-content: center;
  align-items:center;
}

.module-box-footer {
  display:flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0px;
  margin-bottom: 16px;
  height: 24px;
  width: 100%;
}

.controls {
    width: 50px;
    display:flex;
    flex-direction: row;
    justify-content: space-around;
}

.indicator {
    height: 20px;
    width:20px;
    border: 1px solid #0f4c75;
    background-color: transparent;
    transition: background-color 0.3s linear;
    border-radius: 10px;
}

.indicator.active {
  background-color: #0f4c75;
}

.mb-light {
  color: white;
  background-color: white;
}

.module-box.sortable-chosen {
	background-color: @disabled-background;
	border-color: @disabled-background;
}

.modules-container:not(.dragging) .module-box:hover {
	border-color: @text-muted;
}

.hovered-box {
  background-color: @light-bg;
}

.octicon-chevron-down {
  font-size: 14px;
  padding: 4px 6px 2px 6px;
  border-radius: 4px;

  &:hover {
	background: @btn-bg;
  }
}

.octicon-chevron-down:hover {
  cursor: pointer;
}



.module-box-link {
  flex: 1;
  padding-top: 5px;
  padding-bottom: 5px;
  text-decoration: none;
  --moz-text-decoration-line: none;
}

.icon-box {
  padding: 15px;
  width: 54px;
  display: flex;
  justify-content: center;
}

.icon {
  font-size: 24px;
}

.open-notification {
  top: -2px;
}

.shortcut-tag {
  margin-right: 5px;
}

.drag-handle {
  font-size: 12px;
}


</style>
