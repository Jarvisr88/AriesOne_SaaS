&lt;template>
  &lt;div class="security-policy-manager">
    &lt;div class="header">
      &lt;h2>Security Policy Management&lt;/h2>
      &lt;v-btn color="primary" @click="openCreateDialog">
        Create Policy
      &lt;/v-btn>
    &lt;/div>

    &lt;v-tabs v-model="activeTab" class="mb-6">
      &lt;v-tab v-for="type in policyTypes" :key="type.value">
        {{ type.label }}
      &lt;/v-tab>
    &lt;/v-tabs>

    &lt;v-card>
      &lt;v-data-table
        :headers="headers"
        :items="filteredPolicies"
        :loading="loading"
        class="elevation-1"
      >
        &lt;template v-slot:item.is_enabled="{ item }">
          &lt;v-switch
            v-model="item.is_enabled"
            @change="togglePolicy(item)"
            :disabled="loading"
          >&lt;/v-switch>
        &lt;/template>

        &lt;template v-slot:item.priority="{ item }">
          &lt;v-chip :color="getPriorityColor(item.priority)">
            {{ getPriorityLabel(item.priority) }}
          &lt;/v-chip>
        &lt;/template>

        &lt;template v-slot:item.actions="{ item }">
          &lt;v-icon small class="mr-2" @click="editPolicy(item)">
            mdi-pencil
          &lt;/v-icon>
          &lt;v-icon small @click="deletePolicy(item)">
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
                  &lt;v-select
                    v-model="editedItem.policy_type"
                    :items="policyTypes"
                    item-text="label"
                    item-value="value"
                    label="Policy Type"
                    required
                    :rules="[v => !!v || 'Policy type is required']"
                    @change="updatePolicyTemplate"
                  >&lt;/v-select>
                &lt;/v-col>

                &lt;v-col cols="12">
                  &lt;v-textarea
                    v-model="editedItem.description"
                    label="Description"
                  >&lt;/v-textarea>
                &lt;/v-col>

                &lt;v-col cols="12">
                  &lt;v-slider
                    v-model="editedItem.priority"
                    label="Priority"
                    min="0"
                    max="100"
                    thumb-label="always"
                  >&lt;/v-slider>
                &lt;/v-col>

                &lt;v-col cols="12">
                  &lt;v-switch
                    v-model="editedItem.is_enabled"
                    label="Enabled"
                  >&lt;/v-switch>
                &lt;/v-col>

                &lt;v-col cols="12">
                  &lt;div class="settings-editor">
                    &lt;h3>Policy Settings&lt;/h3>
                    &lt;component
                      :is="currentPolicyEditor"
                      v-model="editedItem.settings"
                      :rules="settingsRules"
                    >&lt;/component>
                  &lt;/div>
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
        &lt;v-card-title class="text-h5">Delete Policy&lt;/v-card-title>
        &lt;v-card-text>
          Are you sure you want to delete this security policy?
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
import PasswordPolicyEditor from './policy-editors/PasswordPolicyEditor.vue'
import SessionPolicyEditor from './policy-editors/SessionPolicyEditor.vue'
import RateLimitPolicyEditor from './policy-editors/RateLimitPolicyEditor.vue'

export default {
  name: 'SecurityPolicyManager',

  components: {
    PasswordPolicyEditor,
    SessionPolicyEditor,
    RateLimitPolicyEditor
  },

  setup() {
    const store = useStore()
    const activeTab = ref(0)
    const dialog = ref(false)
    const deleteDialog = ref(false)
    const valid = ref(true)
    const loading = ref(false)
    const form = ref(null)

    const policyTypes = [
      { label: 'Password Policies', value: 'password' },
      { label: 'Session Policies', value: 'session' },
      { label: 'Rate Limiting', value: 'rate-limit' }
    ]

    const headers = [
      { text: 'Name', value: 'name' },
      { text: 'Description', value: 'description' },
      { text: 'Priority', value: 'priority' },
      { text: 'Enabled', value: 'is_enabled' },
      { text: 'Actions', value: 'actions', sortable: false }
    ]

    const defaultItem = {
      name: '',
      policy_type: '',
      description: '',
      settings: {},
      is_enabled: true,
      priority: 0
    }

    const editedItem = ref({ ...defaultItem })
    const editedIndex = ref(-1)
    const policies = ref([])

    const snackbar = ref({
      show: false,
      text: '',
      color: 'success'
    })

    const nameRules = [
      v => !!v || 'Name is required',
      v => v.length <= 255 || 'Name must be less than 255 characters'
    ]

    const settingsRules = computed(() => {
      return [
        v => {
          const requiredFields = getRequiredFields(editedItem.value.policy_type)
          for (const field of requiredFields) {
            if (!v[field]) {
              return `${field} is required`
            }
          }
          return true
        }
      ]
    })

    const formTitle = computed(() => {
      return editedIndex.value === -1 ? 'New Security Policy' : 'Edit Security Policy'
    })

    const filteredPolicies = computed(() => {
      const type = policyTypes[activeTab.value].value
      return policies.value.filter(p => p.policy_type === type)
    })

    const currentPolicyEditor = computed(() => {
      switch (editedItem.value.policy_type) {
        case 'password':
          return 'password-policy-editor'
        case 'session':
          return 'session-policy-editor'
        case 'rate-limit':
          return 'rate-limit-policy-editor'
        default:
          return null
      }
    })

    function getRequiredFields(policyType) {
      switch (policyType) {
        case 'password':
          return ['min_length']
        case 'session':
          return ['max_session_duration']
        case 'rate-limit':
          return ['requests_per_minute']
        default:
          return []
      }
    }

    function getPolicyTemplate(policyType) {
      switch (policyType) {
        case 'password':
          return {
            min_length: 8,
            require_uppercase: true,
            require_lowercase: true,
            require_numbers: true,
            require_special: true,
            special_chars: '!@#$%^&*()_+-=[]{}|;:,.<>?'
          }
        case 'session':
          return {
            max_session_duration: 24 * 60 * 60,
            idle_timeout: 30 * 60,
            max_concurrent_sessions: 5,
            require_mfa: false
          }
        case 'rate-limit':
          return {
            requests_per_minute: 60,
            burst_size: 10,
            throttle_by: 'user'
          }
        default:
          return {}
      }
    }

    function updatePolicyTemplate() {
      editedItem.value.settings = getPolicyTemplate(editedItem.value.policy_type)
    }

    function getPriorityColor(priority) {
      if (priority >= 80) return 'red'
      if (priority >= 50) return 'orange'
      if (priority >= 20) return 'yellow'
      return 'green'
    }

    function getPriorityLabel(priority) {
      if (priority >= 80) return 'Critical'
      if (priority >= 50) return 'High'
      if (priority >= 20) return 'Medium'
      return 'Low'
    }

    async function initialize() {
      loading.value = true
      try {
        const response = await fetch('/api/v1/security-policies/')
        policies.value = await response.json()
      } catch (error) {
        showError('Failed to load security policies')
      }
      loading.value = false
    }

    async function togglePolicy(item) {
      try {
        const response = await fetch(`/api/v1/security-policies/${item.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            is_enabled: item.is_enabled
          })
        })

        if (!response.ok) throw new Error('Failed to update policy')
        
        showSuccess('Policy updated successfully')
      } catch (error) {
        item.is_enabled = !item.is_enabled // Revert the toggle
        showError('Failed to update policy')
      }
    }

    function editPolicy(item) {
      editedIndex.value = policies.value.indexOf(item)
      editedItem.value = Object.assign({}, item)
      dialog.value = true
    }

    function deletePolicy(item) {
      editedIndex.value = policies.value.indexOf(item)
      editedItem.value = Object.assign({}, item)
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
      })
    }

    async function save() {
      if (!form.value.validate()) return

      try {
        const method = editedIndex.value === -1 ? 'POST' : 'PUT'
        const url = editedIndex.value === -1
          ? '/api/v1/security-policies/'
          : `/api/v1/security-policies/${editedItem.value.id}`

        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(editedItem.value)
        })

        if (!response.ok) throw new Error('Failed to save policy')

        if (editedIndex.value > -1) {
          Object.assign(policies.value[editedIndex.value], editedItem.value)
        } else {
          policies.value.push(await response.json())
        }

        showSuccess(`Policy ${editedIndex.value === -1 ? 'created' : 'updated'} successfully`)
        close()
      } catch (error) {
        showError('Failed to save policy')
      }
    }

    async function deleteItemConfirm() {
      try {
        const response = await fetch(`/api/v1/security-policies/${editedItem.value.id}`, {
          method: 'DELETE'
        })

        if (!response.ok) throw new Error('Failed to delete policy')

        policies.value.splice(editedIndex.value, 1)
        showSuccess('Policy deleted successfully')
        closeDelete()
      } catch (error) {
        showError('Failed to delete policy')
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
      activeTab,
      dialog,
      deleteDialog,
      valid,
      loading,
      form,
      policyTypes,
      headers,
      editedItem,
      policies,
      filteredPolicies,
      currentPolicyEditor,
      snackbar,
      nameRules,
      settingsRules,
      formTitle,
      getPriorityColor,
      getPriorityLabel,
      togglePolicy,
      editPolicy,
      deletePolicy,
      close,
      closeDelete,
      save,
      deleteItemConfirm,
      updatePolicyTemplate
    }
  }
}
&lt;/script>

&lt;style scoped>
.security-policy-manager {
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

.settings-editor {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 16px;
  margin-top: 8px;
}

.settings-editor h3 {
  margin-bottom: 16px;
  color: rgba(0, 0, 0, 0.87);
}
&lt;/style>
