import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { vaultAPI, VaultItem } from '../api/services';
import './VaultPage.css';

export function VaultPage() {
  const [items, setItems] = useState<VaultItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    item_type: 'loadout',
    is_private: true,
  });

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await vaultAPI.list();
      setItems(response.data);
    } catch (error) {
      console.error('Failed to fetch vault items:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await vaultAPI.create(formData);
      setShowCreateModal(false);
      setFormData({ name: '', description: '', item_type: 'loadout', is_private: true });
      fetchItems();
    } catch (error) {
      console.error('Failed to create item:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Delete this item?')) {
      try {
        await vaultAPI.delete(id);
        fetchItems();
      } catch (error) {
        console.error('Failed to delete item:', error);
      }
    }
  };

  return (
    <div className="vault-page">
      <header className="page-header">
        <div className="header-content">
          <Link to="/dashboard" className="back-link">← Back</Link>
          <h1>🔒 Player Vault</h1>
        </div>
      </header>

      <main className="vault-main">
        <div className="vault-actions">
          <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
            + New Item
          </button>
        </div>

        {loading ? (
          <div className="loading">Loading...</div>
        ) : items.length === 0 ? (
          <div className="empty-state">
            <h3>Your vault is empty</h3>
            <p>Store loadouts, clips, achievements, and notes here</p>
          </div>
        ) : (
          <div className="items-grid">
            {items.map((item) => (
              <div key={item.id} className="vault-item">
                <div className="item-header">
                  <h3>{item.name}</h3>
                  <span className={`item-type ${item.item_type}`}>{item.item_type}</span>
                </div>
                {item.description && <p>{item.description}</p>}
                <div className="item-footer">
                  <span className="privacy">
                    {item.is_private ? '🔒 Private' : '👁️ Shared'}
                  </span>
                  <button className="btn-delete" onClick={() => handleDelete(item.id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Item</h2>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Type</label>
                <select
                  value={formData.item_type}
                  onChange={(e) => setFormData({ ...formData, item_type: e.target.value })}
                >
                  <option value="loadout">Loadout</option>
                  <option value="clip">Clip</option>
                  <option value="achievement">Achievement</option>
                  <option value="note">Note</option>
                </select>
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.is_private}
                    onChange={(e) => setFormData({ ...formData, is_private: e.target.checked })}
                  />
                  Private
                </label>
              </div>
              <div className="modal-actions">
                <button type="submit" className="btn-primary">Create</button>
                <button type="button" onClick={() => setShowCreateModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default VaultPage;
