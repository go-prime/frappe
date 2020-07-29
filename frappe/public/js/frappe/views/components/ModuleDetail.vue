<template>
	<div>

		<div v-if="sections.length" class="sections-container">
			<div v-for="(section, index) in sections"
				:key="section.label"
				:class="{'section-box': true, 'alternate-section-box': index % 2 == 0}"
			>
				<h4 class="h4"> {{ section.label }} </h4>
				<h5>Documents in use</h5>
				<div class="link-container">
					<module-link-item v-for="item in withCount(section.items)"
					:key="section.label + item.label"
					:data-youtube-id="item.type==='help' ? item.youtube_id : false"
					v-bind="item"
					>
					</module-link-item>
				</div>
				
				
				<h5>New | Reference Documents</h5>
				<div class="link-container">
					<module-link-item v-for="item in withoutCount(section.items)"
						:key="section.label + item.label"
						:data-youtube-id="item.type==='help' ? item.youtube_id : false"
						v-bind="item"
					>
					</module-link-item>
				</div>
				<h5>Documents With Missing Dependencies</h5>
				<div class="link-container">
					<module-link-item v-for="item in missingDependencies(section.items)"
						:key="section.label + item.label"
						:data-youtube-id="item.type==='help' ? item.youtube_id : false"
						v-bind="item"
					>
					</module-link-item>
				</div>
				
			</div>
		</div>

		<div v-else class="sections-container">
			<div v-for="n in 3" :key="n" class="skeleton-section-box"></div>
		</div>
	</div>
</template>

<script>
import ModuleLinkItem from "./ModuleLinkItem.vue";

export default {
	components: {
		ModuleLinkItem
	},
	props: ['module_name', 'sections'],
	methods: {
		withCount(items) {
			return items.filter((item) => item.count)
		},

		withoutCount(items) {
			return items.filter((item) => !item.count && !(item.dependencies && item.incomplete_dependencies))
		},

		missingDependencies(items) {
			return items.filter((item) => item.dependencies && item.incomplete_dependencies)
		}
	}
}
</script>
<style lang="less" scoped>
.sections-container {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
	column-gap: 15px;
	row-gap: 15px;
	margin-top:36px;
}

.section-box {
	padding: 5px 20px;
	border-radius: 4px;
	color: #0f4c75;
	background-color: #bbe1fa;
	box-shadow: 0px 0px 4px rgba(0,0,0,0.3);
}

.alternate-section-box {
	background-color: white;
}

.skeleton-section-box {
	background-color: #f5f7fa;
	height: 250px;
	border-radius: 4px;
}

.h4 {
	margin-bottom: 15px;
}

.link-container {
	padding-left: 2rem;
}

</style>
