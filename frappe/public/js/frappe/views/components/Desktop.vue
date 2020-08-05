<template>
	<div class="modules-page-container" v-if="home_settings_fetched">
		<div class="modules-section">
			<div 
				class="modules-container" 
				:class="{'dragging': dragging}" 
				ref="modules-container"
				>
				<DeskModuleBox 
					v-for="(mod, index) in all_modules()"
					v-bind="mod" 
					:key="mod.module_name"
					:index="index"
					@customize="show_module_card_customize_dialog(mod)"
					>
				</DeskModuleBox>
			</div>
		</div>
	</div>
</template>

<script>
import DeskModuleBox from "./DeskModuleBox.vue";
import { generate_route } from './utils';

export default {
	components: {
		DeskModuleBox
	},
	data() {
		return {
			module_categories: ['Modules', 'Domains', 'Places', 'Administration'],
			modules: [],
			home_settings_fetched: false,
			dragging: false,
			fetched_module_links: {}
		};
	},
	created() {
		this.fetch_desktop_settings();
	},
	mounted() {
		if (!frappe.utils.is_mobile()) {
			this.setup_sortable();
		}
	},
	methods: {
		log_modules(data) {
			return data;
		},
		all_modules() {
			const module_list = [];
			this.module_categories.forEach(cat =>{
				let cat_modules = this.get_modules_for_category(cat)
				module_list.push(...cat_modules)
			})

			return module_list
		},
		show_module_card_customize_dialog(module) {
			const me = this;
			const d = new frappe.ui.Dialog({
				title: __('Customize Shortcuts'),
				fields: [
					{
						label: __('Shortcuts'),
						fieldname: 'links',
						fieldtype: 'MultiSelectPills',
						get_data: () => {
							const module_links = me.fetched_module_links[module.module_name];
							if (!module_links) {
								return frappe.xcall('frappe.desk.moduleview.get_links_for_module', {
									app: module.app,
									module: module.module_name,
								}).then(links => {
									me.fetched_module_links[module.module_name] = links;
									return links;
								});
							} else {
								return module_links;
							}
						},
						default: module.links.filter(l => !l.hidden).map(l => l.name)
					}
				],
				primary_action_label: __('Save'),
				primary_action: ({ links }) => {
					frappe.call('frappe.desk.moduleview.update_links_for_module', {
						module_name: module.module_name,
						links: links || []
					}).then(r => {
						this.$emit('update-desktop-settings', r.message);
					});
					d.hide();
				}
			});

			d.show();
		},
		setup_sortable() {
			
			let modules_container =this.$refs['modules-container'];
			if(modules_container == undefined){
				setTimeout(this.setup_sortable, 1000)
			}
			
			this.sortable = new Sortable(modules_container, {
				animation: 150,
				onStart: () => this.dragging = true,
				onEnd: () => {
					this.dragging = false;
					let modules = Array.from(modules_container.querySelectorAll('.module-box'))
						.map(node => node.dataset.moduleName);

					this.$emit('module-order-change', {
						modules
					});
				}
			})
		},
		fetch_desktop_settings() {
			frappe.call('frappe.desk.moduleview.get_desktop_settings')
				.then(r => {
					if (r.message) {
						this.update_desktop_settings(r.message);
						this.home_settings_fetched = true;
					}
				});
		},
		update_desktop_settings(desktop_settings) {
			this.modules = this.add_routes_for_module_links(desktop_settings);
		},
		add_routes_for_module_links(user_settings) {
			for (let category in user_settings) {
				user_settings[category] = user_settings[category].map(m => {
					m.links = (m.links || []).map(link => {
						link.route = generate_route(link);
						return link;
					});
					return m;
				});
			}
			return user_settings;
		},
		update_module_order({ module_category, modules }) {
			frappe.call('frappe.desk.moduleview.update_modules_order', { module_category, modules });
		},
		get_modules_for_category(category) {
			return this.modules[category] || [];
		},
		show_hide_cards_dialog() {
			frappe.call('frappe.desk.moduleview.get_options_for_show_hide_cards')
				.then(r => {
					let { user_options, global_options } = r.message;

					let user_value = `User (${frappe.session.user})`
					let fields = [
						{
							label: __('Setup For'),
							fieldname: 'setup_for',
							fieldtype: 'Select',
							options: [
								{
									label: __('User ({0})', [frappe.session.user]),
									value: user_value
								},
								{
									label: __('Everyone'),
									value: 'Everyone'
								}
							],
							default: user_value,
							depends_on: doc => frappe.user_roles.includes('System Manager'),
							onchange() {
								let value = d.get_value('setup_for');
								let field = d.get_field('setup_for');
								let description = value === 'Everyone' ? __('Hide cards for all users') : '';
								field.set_description(description);
							}
						}
					];

					let user_section = this.module_categories.map(category => {
						let options = user_options.filter(m => m.category === category);
						return {
							label: category,
							fieldname: `user:${category}`,
							fieldtype: 'MultiCheck',
							options,
							columns: 2
						}
					}).filter(f => f.options.length > 0);

					user_section = [
						{
							fieldname: 'user_section',
							fieldtype: 'Section Break',
							depends_on: doc => doc.setup_for === user_value
						}
					].concat(user_section);

					let global_section = this.module_categories.map(category => {
						let options = global_options.filter(m => m.category === category);
						return {
							label: category,
							fieldname: `global:${category}`,
							fieldtype: 'MultiCheck',
							options,
							columns: 2
						}
					}).filter(f => f.options.length > 0);

					global_section = [
						{
							fieldname: 'global_section',
							fieldtype: 'Section Break',
							depends_on: doc => doc.setup_for === 'Everyone'
						}
					].concat(global_section);

					fields = fields.concat(user_section, global_section);

					let old_values = null;
					const d = new frappe.ui.Dialog({
						title: __('Show / Hide Cards'),
						fields: fields,
						primary_action_label: __('Save'),
						primary_action: (values) => {
							if (values.setup_for === 'Everyone') {
								this.update_global_modules(d);
							} else {
								this.update_user_modules(d, old_values);
							}
						}
					});

					d.show();

					// deepcopy
					old_values = JSON.parse(JSON.stringify(d.get_values()));
				});
		},

		update_user_modules(d, old_values) {
			let new_values = d.get_values();
			let category_map = {};
			for (let category of this.module_categories) {
				let old_modules = old_values[`user:${category}`] || [];
				let new_modules = new_values[`user:${category}`] || [];

				let removed = old_modules.filter(module => !new_modules.includes(module));
				let added = new_modules.filter(module => !old_modules.includes(module));

				category_map[category] = { added, removed };
			}

			frappe.call({
				method: 'frappe.desk.moduleview.update_hidden_modules',
				args: { category_map },
				btn: d.get_primary_btn()
			}).then(r => {
				this.update_desktop_settings(r.message);
				d.hide();
			});
		},

		update_global_modules(d) {
			let blocked_modules = [];
			for (let category of this.module_categories) {
				let field = d.get_field(`global:${category}`);
				if (field) {
					let unchecked_options = field.get_unchecked_options();
					blocked_modules = blocked_modules.concat(unchecked_options);
				}
			}

			frappe.call({
				method: 'frappe.desk.moduleview.update_global_hidden_modules',
				args: {
					modules: blocked_modules
				},
				btn: d.get_primary_btn()
			}).then(r => {
				this.update_desktop_settings(r.message);
				d.hide();
			});
		}
	}
}
</script>

<style lang="less" scoped>
.modules-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  grid-auto-rows: minmax(62px, 1fr);
  column-gap: 8px;
  row-gap: 8px;
  align-items: center;
}

.modules-page-container {
	position: relative;
	margin-top: 70px;
	margin-bottom: 30px;
	padding-top: 1px;
}

.modules-section {
	position: relative;
}

.btn-show-hide {
	position: absolute;
	right: 0;
	top: 39px;
	z-index: 1;
}

.toolbar-underlay {
	margin: 70px;
}
</style>

