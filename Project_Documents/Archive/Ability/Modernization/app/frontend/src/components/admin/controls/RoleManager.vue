&lt;template>
  &lt;div class="role-manager">
    &lt;div class="header">
      &lt;h2>Role Management&lt;/h2>
      &lt;v-btn color="primary" @click="openCreateDialog">
        Create Role
      &lt;/v-btn>
    &lt;/div>

    &lt;v-card>
      &lt;v-card-title>
        &lt;v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        >&lt;/v-text-field>
      &lt;/v-card-title>

      &lt;v-data-table
        :headers="headers"
        :items="roles"
        :search="search"
        :loading="loading"
        class="elevation-1"
      >
        &lt;template v-slot:item.is_system_role="{ item }">
          &lt;v-chip :color="item.is_system_role ? 'primary' : 'default'">
            {{ item.is_system_role ? 'System' : 'Custom' }}
          &lt;/v-chip>
        &lt;/template>

        &lt;template v-slot:item.permissions="{ item }">
          &lt;v-chip-group>
            &lt;v-chip
              v-for="permission in item.permissions.slice(0, 3)"
              :key="permission.id"
              small
            >
              {{ permission.name }}
            &lt;/v-chip>
            &lt;v-chip small v-if="item.permissions.length > 3">
              +{{ item.permissions.length - 3 }} more
            &lt;/v-chip>
          &lt;/v-chip-group>
        &lt;/template>

        &lt;template v-slot:item.actions="{ item }">
          &lt;v-icon
            small
            class="mr-2"
            @click="editRole(item)"
            :disabled="item.is_system_role"
          >
            mdi-pencil
          &lt;/v-icon>
          &lt;v-icon
            small
            @click="deleteRole(item)"
            :disabled="item.is_system_role"
          >
            mdi-delete
          &lt;/v-icon>
        &lt;/template>
      &lt;/v-data-table>
    &lt;/v-card>

    &lt;!-- Create/Edit Dialog -->
    &lt;v-dialog v-model="dialog" max-width="800px">
      &lt;v-card>
        &lt;v-card-title>
          &lt;span class="text-h5">{{ formTitle }}&lt;/span>
        &lt;/v-card-title>

        &lt;v-card-text>
          &lt;v-container>
            &lt;v-form ref="form" v-model="valid">
              &lt;v-row>
                &lt;v-col cols="12">
                  &lt;v-text-field
                    v-model="editedItem.name"
                    label="Name"
                    :rules="nameRules"
                    required
                  >&lt;/v-text-field>
                &lt;/v-col>

                &lt;v-col cols="12">
                  &lt;v-textarea
                    v-model="editedItem.description"
                    label="Description"
                  >&lt;/v-textarea>
                &lt;/v-col>

                &lt;v-col cols="12">
                  &lt;v-select
                    v-model="editedItem.parent_role_id"
                    :items="parentRoleOptions"
                    item-text="name"
                    item-value="id"
                    label="Parent Role"
                    clearable
                  >&lt;/v-select>
                &lt;/v-col>

                &lt;v-col cols="12">
                  &lt;v-select
                    v-model="editedItem.permission_ids"
                    :items="permissions"
                    item-text="name"
                    item-value="id"
                    label="Permissions"
                    multiple
                    chips
                    :rules="permissionRules"
                  >
                    &lt;template v-slot:selection="{ item, index }">
                      &lt;v-chip v-if="index < 3">
                        &lt;span>{{ item.name }}&lt;/span>
                      &lt;/v-chip>
                      &lt;span
                        v-if="index === 3"
                        class="grey--text caption"
                      >
                        (+{{ editedItem.permission_ids.length - 3 }} others)
                      &lt;/span>
                    &lt;/template>
                  &lt;/v-select>
                &lt;/v-col>

                &lt;v-col cols="12">
                  &lt;v-textarea
                    v-model="settingsText"
                    label="Settings (JSON)"
                    :rules="jsonRules"
                  >&lt;/v-textarea>
                &lt;/v-col>
              &lt;/v-row>
            &lt;/v-form>
          &lt;/v-container>
        &lt;/v-card-text>

        &lt;v-card-actions>
          &lt;v-spacer>&lt;/v-spacer>
          &lt;v-btn color="blue darken-1" text @click="close">
            Cancel
          &lt;/v-btn>
          &lt;v-btn
            color="blue darken-1"
            text
            @click="save"
            :disabled="!valid"
          >
            Save
          &lt;/v-btn>
        &lt;/v-card-actions>
      &lt;/v-card>
    &lt;/v-dialog>

    &lt;!-- Delete Confirmation -->
    &lt;v-dialog v-model="deleteDialog" max-width="400px">
      &lt;v-card>
        &lt;v-card-title class="text-h5">Delete Role&lt;/v-card-title>
        &lt;v-card-text>
          Are you sure you want to delete this role?
          &lt;div class="warning mt-3" v-if="hasAssignedUsers">
            Warning: This role is currently assigned to users.
            Deleting it will remove these permissions from those users.
          &lt;/div>
        &lt;/v-card-text>
        &lt;v-card-actions>
          &lt;v-spacer>&lt;/v-spacer>
          &lt;v-btn color="blue darken-1" text @click="closeDelete">Cancel&lt;/v-btn>
          &lt;v-btn color="red darken-1" text @click="deleteItemConfirm">Delete&lt;/v-btn>
        &lt;/v-card-actions>
      &lt;/v-card>
    &lt;/v-dialog>

    &lt;!-- Snackbar for notifications -->
    &lt;v-snackbar v-model="snackbar.show" :color="snackbar.color">
      {{ snackbar.text }}
      &lt;template v-slot:action="{ attrs }">
        &lt;v-btn text v-bind="attrs" @click="snackbar.show = false">
          Close
        &lt;/v-btn>
      &lt;/template>
    &lt;/v-snackbar>
  &lt;/div>
&lt;/template>

&lt;script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'RoleManager',

  setup() {
    const store = useStore()
    const search = ref('')
    const dialog = ref(false)
    const deleteDialog = ref(false)
    const valid = ref(true)
    const loading = ref(false)
    const form = ref(null)
    const hasAssignedUsers = ref(false)

    const headers = [
      { text: 'Name', value: 'name' },
      { text: 'Description', value: 'description' },
      { text: 'Type', value: 'is_system_role' },
      { text: 'Permissions', value: 'permissions' },
      { text: 'Actions', value: 'actions', sortable: false }
    ]

    const defaultItem = {
      name: '',
      description: '',
      parent_role_id: null,
      permission_ids: [],
      settings: {}
    }

    const editedItem = ref({ ...defaultItem })
    const editedIndex = ref(-1)
    const roles = ref([])
    const permissions = ref([])

    const snackbar = ref({
      show: false,
      text: '',
      color: 'success'
    })

    const nameRules = [
      v => !!v || 'Name is required',
      v => v.length <= 255 || 'Name must be less than 255 characters'
    ]

    const permissionRules = [
      v => v.length > 0 || 'At least one permission is required'
    ]

    const jsonRules = [
      v => {
        if (!v) return true
        try {
          JSON.parse(v)
          return true
        } catch (e) {
          return 'Must be valid JSON'
        }
      }
    ]

    const formTitle = computed(() => {
      return editedIndex.value === -1 ? 'New Role' : 'Edit Role'
    })

    const parentRoleOptions = computed(() => {
      return roles.value.filter(role => role.id !== editedItem.value.id)
    })

    const settingsText = computed({
      get: () => {
        return editedItem.value.settings
          ? JSON.stringify(editedItem.value.settings, null, 2)
          : '{}'
      },
      set: (val) => {
        try {
          editedItem.value.settings = val ? JSON.parse(val) : {}
        } catch (e) {
          // Invalid JSON - will be caught by validation
        }
      }
    })

    async function initialize() {
      loading.value = true
      try {
        const [rolesResponse, permissionsResponse] = await Promise.all([
          fetch('/api/v1/roles/'),
          fetch('/api/v1/permissions/')
        ])
        roles.value = await rolesResponse.json()
        permissions.value = await permissionsResponse.json()
      } catch (error) {
        showError('Failed to load data')
      }
      loading.value = false
    }

    async function checkRoleAssignments(roleId) {
      try {
        const response = await fetch(`/api/v1/roles/${roleId}/assignments`)
        const data = await response.json()
        hasAssignedUsers.value = data.user_count > 0
      } catch (error) {
        console.error('Failed to check role assignments:', error)
        hasAssignedUsers.value = false
      }
    }

    function editRole(item) {
      editedIndex.value = roles.value.indexOf(item)
      editedItem.value = Object.assign({}, item)
      dialog.value = true
    }

    async function deleteRole(item) {
      editedIndex.value = roles.value.indexOf(item)
      editedItem.value = Object.assign({}, item)
      await checkRoleAssignments(item.id)
      deleteDialog.value = true
    }

    function close() {
      dialog.value = false
      nextTick(() => {
        editedItem.value = Object.assign({}, defaultItem)
        editedIndex.value = -1
        form.value?.reset()
      })
    }

    function closeDelete() {
      deleteDialog.value = false
      nextTick(() => {
        editedItem.value = Object.assign({}, defaultItem)
        editedIndex.value = -1
        hasAssignedUsers.value = false
      })
    }

    async function save() {
      if (!form.value.validate()) return

      try {
        const method = editedIndex.value === -1 ? 'POST' : 'PUT'
        const url = editedIndex.value === -1
          ? '/api/v1/roles/'
          : `/api/v1/roles/${editedItem.value.id}`

        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(editedItem.value)
        })

        if (!response.ok) throw new Error('Failed to save role')

        if (editedIndex.value > -1) {
          Object.assign(roles.value[editedIndex.value], editedItem.value)
        } else {
          roles.value.push(await response.json())
        }

        showSuccess(`Role ${editedIndex.value === -1 ? 'created' : 'updated'} successfully`)
        close()
      } catch (error) {
        showError('Failed to save role')
      }
    }

    async function deleteItemConfirm() {
      try {
        const response = await fetch(`/api/v1/roles/${editedItem.value.id}`, {
          method: 'DELETE'
        })

        if (!response.ok) throw new Error('Failed to delete role')

        roles.value.splice(editedIndex.value, 1)
        showSuccess('Role deleted successfully')
        closeDelete()
      } catch (error) {
        showError('Failed to delete role')
      }
    }

    function showSuccess(text) {
      snackbar.value = {
        show: true,
        text,
        color: 'success'
      }
    }

    function showError(text) {
      snackbar.value = {
        show: true,
        text,
        color: 'error'
      }
    }

    onMounted(() => {
      initialize()
    })

    return {
      search,
      dialog,
      deleteDialog,
      valid,
      loading,
      form,
      headers,
      editedItem,
      roles,
      permissions,
      hasAssignedUsers,
      snackbar,
      nameRules,
      permissionRules,
      jsonRules,
      formTitle,
      parentRoleOptions,
      settingsText,
      editRole,
      deleteRole,
      close,
      closeDelete,
      save,
      deleteItemConfirm
    }
  }
}
&lt;/script>

&lt;style scoped>
.role-manager {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.v-data-table {
  margin-top: 20px;
}

.warning {
  color: #ff5252;
  font-weight: 500;
}
&lt;/style>
