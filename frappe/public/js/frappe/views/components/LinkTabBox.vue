<template>
    <div class="link-container">
        <ul class="list-group">
            <li class="list-group-item" v-for="item of dropdownItems" :key="item.label" :class="item.class || null">
                <a v-if="item.route" :href="item.route">{{ item.label }}</a>
                <span v-else @click="item.action"> <i class="fa fa-cog" aria-hidden="true"></i> {{ item.label }}</span>
            </li>
        </ul>
    </div>
</template>

<script>

export default {
  name: "LinkTab",  
  props: {
    items: {
      type: Array,
      default: () => []
    },
    
  },
  data() {
    return {
      isOpen: false
    };
  },
  computed: {
    dropdownItems() {
      return (this.items || []).map(item => {
        if (typeof item === "string") {
          return {
            label: item,
            action: console.log
          };
        }
        if (!item.action && item.route) {
          item.action = this.setRoute.bind(this, item.route);
        }
        return item;
      });
    }
  },
  methods: {
    setRoute(route) {
      this.$router.push(route);
    }
  }
};
</script>
<style scoped>

a {
  font-size: 12px;
  text-decoration: none;
}
.list-group-item {
    border: 0px
}

.link-container {
    height: 100%;
    overflow-y: scroll;
}

/* width */
.link-container::-webkit-scrollbar {
    width: 8px;
}

/* Track */
.link-container::-webkit-scrollbar-track {
    background: #f1f1f1;
}

/* Handle */
.link-container::-webkit-scrollbar-thumb {
    background: #3282b8;
    border-radius: 4px;
}

/* Handle on hover */
.link-container::-webkit-scrollbar-thumb:hover {
    background: #0f4c75;
}
</style>
