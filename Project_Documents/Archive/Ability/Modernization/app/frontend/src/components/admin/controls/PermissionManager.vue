&lt;template>
  &lt;div class="permission-manager">
    &lt;div class="header">
      &lt;h2>Permission Management&lt;/h2>
      &lt;v-btn color="primary" @click="openCreateDialog">
        Create Permission
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
        :items="permissions"
        :search="search"
        :loading="loading"
        class="elevation-1"
      >
        &lt;template v-slot:item.actions="{ item }">
          &lt;v-icon small class="mr-2" @click="editPermission(item)">
            mdi-pencil
          &lt;/v-icon>
          &lt;v-icon small @click="deletePermission(item)">
            mdi-delete
          &lt;/v-icon>
        &lt;/template>
      &lt;/v-data-table>
    &lt;/v-card>

    &lt;!-- Create/Edit Dialog -->
    &lt;v-dialog v-model="dialog" max-width="600px">
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
                  &lt;v-select
                    v-model="editedItem.resource_type"
                    :items="resourceTypes"
                    label="Resource Type"
                    required
                  >&lt;/v-select>
                &lt;/v-col>

                &lt;v-col cols="12">
                  &lt;v-text-field
                    v-model="editedItem.action"
                    label="Action"
                    :rules="actionRules"
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
                  &lt;v-textarea
                    v-model="conditionsText"
                    label="Conditions (JSON)"
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
        &lt;v-card-title class="text-h5">Delete Permission&lt;/v-card-title>
        &lt;v-card-text>
          Are you sure you want to delete this permission?
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
  name: 'PermissionManager',

  setup() {
    const store = useStore()
    const search = ref('')
    const dialog = ref(false)
    const deleteDialog = ref(false)
    const valid = ref(true)
    const loading = ref(false)
    const form = ref(null)

    const headers = [
      { text: 'Name', value: 'name' },
      { text: 'Resource Type', value: 'resource_type' },
      { text: 'Action', value: 'action' },
      { text: 'Description', value: 'description' },
      { text: 'Actions', value: 'actions', sortable: false }
    ]

    const defaultItem = {
      name: '',
      resource_type: '',
      action: '',
      description: '',
      conditions: null
    }

    const editedItem = ref({ ...defaultItem })
    const editedIndex = ref(-1)
    const permissions = ref([])
    const resourceTypes = ref([
      'CALENDAR',
      'EVENT',
      'USER',
      'GROUP',
      'ROLE',
      'COMPANY',
      'REPORT',
      'SETTING'
    ])

    const snackbar = ref({
      show: false,
      text: '',
      color: 'success'
    })

    const nameRules = [
      v => !!v || 'Name is required',
      v => v.length <= 255 || 'Name must be less than 255 characters'
    ]

    const actionRules = [
      v => !!v || 'Action is required',
      v => v.length <= 255 || 'Action must be less than 255 characters'
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
      return editedIndex.value === -1 ? 'New Permission' : 'Edit Permission'
    })

    const conditionsText = computed({
      get: () => {
        return editedItem.value.conditions
          ? JSON.stringify(editedItem.value.conditions, null, 2)
          : ''
      },
      set: (val) => {
        try {
          editedItem.value.conditions = val ? JSON.parse(val) : null
        } catch (e) {
          // Invalid JSON - will be caught by validation
        }
      }
    })

    async function initialize() {
      loading.value = true
      try {
        const response = await fetch('/api/v1/permissions/')
        permissions.value = await response.json()
      } catch (error) {
        showError('Failed to load permissions')
      }
      loading.value = false
    }

    function editPermission(item) {
      editedIndex.value = permissions.value.indexOf(item)
      editedItem.value = Object.assign({}, item)
      dialog.value = true
    }

    function deletePermission(item) {
      editedIndex.value = permissions.value.indexOf(item)
      editedItem.value = Object.assign({}, item)
      deleteDialog.value = true
    }

    function close() {
      dialog.value = false
      nextTick(() => {
        editedItem.value = Object.assign({}, defaultItem)
        editedIndex.value = -1
      })
    }

    function closeDelete() {
      deleteDialog.value = false
      nextTick(() => {
        editedItem.value = Object.assign({}, defaultItem)
        editedIndex.value = -1
      })
    }

    async function save() {
      if (!form.value.validate()) return

      try {
        const method = editedIndex.value === -1 ? 'POST' : 'PUT'
        const url = editedIndex.value === -1
          ? '/api/v1/permissions/'
          : `/api/v1/permissions/${editedItem.value.id}`

        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(editedItem.value)
        })

        if (!response.ok) throw new Error('Failed to save permission')

        if (editedIndex.value > -1) {
          Object.assign(permissions.value[editedIndex.value], editedItem.value)
        } else {
          permissions.value.push(await response.json())
        }

        showSuccess(`Permission ${editedIndex.value === -1 ? 'created' : 'updated'} successfully`)
        close()
      } catch (error) {
        showError('Failed to save permission')
      }
    }

    async function deleteItemConfirm() {
      try {
        const response = await fetch(`/api/v1/permissions/${editedItem.value.id}`, {
          method: 'DELETE'
        })

        if (!response.ok) throw new Error('Failed to delete permission')

        permissions.value.splice(editedIndex.value, 1)
        showSuccess('Permission deleted successfully')
        closeDelete()
      } catch (error) {
        showError('Failed to delete permission')
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
      permissions,
      resourceTypes,
      snackbar,
      nameRules,
      actionRules,
      jsonRules,
      formTitle,
      conditionsText,
      editPermission,
      deletePermission,
      close,
      closeDelete,
      save,
      deleteItemConfirm
    }
  }
}
&lt;/script>

&lt;style scoped>
.permission-manager {
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
&lt;/style>
